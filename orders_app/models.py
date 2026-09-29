"""Database models for customer orders."""

from django.conf import settings
from django.db import models
from offers_app.models import OfferDetail


class Order(models.Model):
    """Stores a snapshot of an offer detail purchased by a customer."""

    class Status(models.TextChoices):
        """Available processing states of an order."""

        IN_PROGRESS = "in_progress", "In progress"
        COMPLETED = "completed", "Completed"
        CANCELLED = "cancelled", "Cancelled"

    customer_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="customer_orders",
    )
    business_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="business_orders",
    )
    title = models.CharField(max_length=100)
    revisions = models.IntegerField()
    delivery_time_in_days = models.IntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    features = models.JSONField(default=list)
    offer_type = models.CharField(
        max_length=20,
        choices=OfferDetail.TYPE_CHOICES,
    )
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.IN_PROGRESS,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        """Defines human-readable names and default ordering."""

        verbose_name = "Order"
        verbose_name_plural = "Orders"
        ordering = ["-updated_at"]

    def __str__(self):
        """Return a readable representation of the order."""
        return f"Order {self.pk}: {self.title}"
