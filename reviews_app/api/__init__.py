from auth_app.models import UserProfile


def validate_business_user(self, value):
    """Allow reviews only for users with a business profile."""
    profile = getattr(value, "profile", None)
    if profile is None or profile.type != UserProfile.BUSINESS:
        raise serializers.ValidationError("Reviews can only target a business user.")
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
