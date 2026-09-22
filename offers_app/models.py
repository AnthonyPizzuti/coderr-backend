"""Database models for offers and offer details."""

from django.db import models
from django.contrib.auth.models import User


class Offer(models.Model):
    """Represents an offer made by a business user.

    Each offer is associated with a business user and can be linked to multiple orders.
    """

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="offers")
    title = models.CharField(max_length=100)
    image = models.FileField(upload_to="offer_images/", blank=True, null=True)
    description = models.TextField(blank=True, default="")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Offer"
        verbose_name_plural = "Offers"
        ordering = ["-updated_at"]

    def __str__(self):
        return f"{self.title} by {self.user.username}"


class OfferDetail(models.Model):
    """Represents the details of an offer, including pricing and delivery information.

    Each offer can have multiple details, allowing for different revisions or variations.
    """

    BASIC = "basic"
    STANDARD = "standard"
    PREMIUM = "premium"
    TYPE_CHOICES = [
        (BASIC, "Basic"),
        (STANDARD, "Standard"),
        (PREMIUM, "Premium"),
    ]

    offer = models.ForeignKey(Offer, on_delete=models.CASCADE, related_name="details")
    title = models.CharField(max_length=100)
    revisions = models.IntegerField()
    delivery_time_in_days = models.IntegerField()
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
    )
    features = models.JSONField(default=list)
    offer_type = models.CharField(
        max_length=50,
        choices=TYPE_CHOICES,
    )

    class Meta:
        verbose_name = "Offer Detail"
        verbose_name_plural = "Offer Details"
        ordering = ["offer_type", "price"]

    def __str__(self):
        return f"{self.title} ({self.offer_type})"
