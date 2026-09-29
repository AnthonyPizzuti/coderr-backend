"""Serializers for business reviews."""

from rest_framework import serializers

from auth_app.models import UserProfile
from reviews_app.models import Review


class ReviewSerializer(serializers.ModelSerializer):
    """Serializes a review for list, create and update.

    Backs ``/api/reviews/``. On update only ``rating`` and
    ``description`` stay writable.
    """

    class Meta:
        model = Review
        fields = [
            "id",
            "business_user",
            "reviewer",
            "rating",
            "description",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["reviewer", "created_at", "updated_at"]

    def __init__(self, *args, **kwargs):
        """Lock ``business_user`` once the review already exists."""
        super().__init__(*args, **kwargs)
        if self.instance is not None:
            self.fields["business_user"].read_only = True

    def validate_business_user(self, value):
        """Allow reviews only for users with a business profile."""
        profile = getattr(value, "profile", None)
        if profile is None or profile.type != UserProfile.BUSINESS:
            raise serializers.ValidationError(
                "Reviews can only target a business user."
            )
        return value

    def validate(self, attrs):
        """Reject a second review of the same business user."""
        if self.instance is not None:
            return attrs
        reviewer = self.context["request"].user
        already_exists = Review.objects.filter(
            business_user=attrs["business_user"],
            reviewer=reviewer,
        ).exists()
        if already_exists:
            raise serializers.ValidationError(
                "You have already reviewed this business user."
            )
        return attrs
