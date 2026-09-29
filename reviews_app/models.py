"""Database models for business reviews."""

from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models


class Review(models.Model):
    """Stores a customer's review of a business user."""

    business_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="received_reviews",
    )
    reviewer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="written_reviews",
    )
    rating = models.PositiveSmallIntegerField(
        validators=[
            MinValueValidator(1),
            MaxValueValidator(5),
        ]
    )
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        """Defines ordering and prevents duplicate reviews."""

        verbose_name = "Review"
        verbose_name_plural = "Reviews"
        ordering = ["-updated_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["business_user", "reviewer"],
                name="unique_business_reviewer",
            )
        ]

    def __str__(self):
        """Return a readable representation of the review."""

        return (
            f"Review by {self.reviewer.username} " f"for {self.business_user.username}"
        )
