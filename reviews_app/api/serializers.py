"""Serializers for business reviews."""

from rest_framework import serializers

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
