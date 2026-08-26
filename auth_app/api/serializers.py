"""Serializers for user registration and authentication."""

from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers

from auth_app.models import UserProfile


class RegistrationSerializer(serializers.ModelSerializer):
    """Validates the registration payload and creates user and profile.

    Backs ``POST /api/registration/``. The account type is not stored on
    the ``User`` itself but on the linked ``UserProfile``.
    """

    repeated_password = serializers.CharField(write_only=True)
    type = serializers.ChoiceField(choices=UserProfile.TYPE_CHOICES)

    class Meta:
        model = User
        fields = ["username", "email", "password", "repeated_password", "type"]
        extra_kwargs = {
            "password": {"write_only": True},
            "email": {"required": True},
        }

    def validate_email(self, value):
        """Reject the address if it is already registered.

        Django's ``User.email`` has no uniqueness constraint on database
        level, so it has to be enforced here.
        """
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("Email is already in use.")
        return value

    def validate(self, data):
        """Ensure both password fields are identical."""
        if data["password"] != data["repeated_password"]:
            raise serializers.ValidationError("Passwords do not match.")
        return data

    def create(self, validated_data):
        """Create the user with a hashed password and its profile.

        ``create_user`` is used instead of ``create`` so the password is
        hashed rather than stored in plain text.
        """
        user = User.objects.create_user(
            username=validated_data["username"],
            email=validated_data["email"],
            password=validated_data["password"],
        )
        UserProfile.objects.create(user=user, type=validated_data["type"])
        return user

    def validate_password(self, value):
        """Validate the password using Django's built-in validators."""

        validate_password(value)
        return value


class LoginSerializer(serializers.Serializer):
    """Validates username and password against Django's auth backend.

    Backs ``POST /api/login/``. On success the authenticated user is
    placed in ``validated_data`` so the view can issue the token.
    """

    username = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        """Authenticate the credentials and attach the user.

        ``authenticate`` returns ``None`` for wrong credentials as well as
        for inactive accounts; both are reported as one generic error so
        no information about existing usernames leaks.
        """
        user = authenticate(username=data["username"], password=data["password"])
        if not user:
            raise serializers.ValidationError("Invalid credentials.")
        data["user"] = user
        return data


class ProfileSerializer(serializers.ModelSerializer):
    """Serializes a user profile including data from the linked user.

    Backs ``GET`` and ``PATCH`` on ``/api/profile/{pk}/``.
    """

    username = serializers.CharField(source="user.username", read_only=True)
    first_name = serializers.CharField(
        source="user.first_name", required=False, allow_blank=True
    )
    last_name = serializers.CharField(
        source="user.last_name", required=False, allow_blank=True
    )
    email = serializers.EmailField(
        source="user.email", required=False, allow_blank=True
    )

    class Meta:
        model = UserProfile
        fields = [
            "user",
            "username",
            "first_name",
            "last_name",
            "file",
            "location",
            "tel",
            "description",
            "working_hours",
            "type",
            "email",
            "created_at",
        ]
        read_only_fields = ["user", "type", "created_at"]

    def update(self, instance, validated_data):
        """Write the nested user fields before updating the profile."""
        user_data = validated_data.pop("user", {})
        for attr, value in user_data.items():
            setattr(instance.user, attr, value)
        instance.user.save()
        return super().update(instance, validated_data)


class BusinessProfileSerializer(ProfileSerializer):
    """Serializes a business profile for the list view.

    Backs ``GET /api/profiles/business/``. Unlike ``ProfileSerializer``
    it omits ``email`` and ``created_at``, which the list does not expose.
    """

    class Meta(ProfileSerializer.Meta):
        fields = [
            "user",
            "username",
            "first_name",
            "last_name",
            "file",
            "location",
            "tel",
            "description",
            "working_hours",
            "type",
        ]
        read_only_fields = ["user", "type"]


class CustomerProfileSerializer(ProfileSerializer):
    """Serializes the customer profile."""

    uploaded_at = serializers.DateTimeField(source="created_at", read_only=True)

    class Meta(ProfileSerializer.Meta):
        fields = [
            "user",
            "username",
            "first_name",
            "last_name",
            "file",
            "uploaded_at",
            "type",
        ]
        read_only_fields = ["user", "type"]
