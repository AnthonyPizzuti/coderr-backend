"""Database models for user profiles."""

from django.contrib.auth.models import User
from django.db import models


class UserProfile(models.Model):
    """Extends Django's ``User`` with the profile data Coderr requires.

    Each user has exactly one profile, created during registration. The
    account type decides whether the user may publish offers.
    """

    CUSTOMER = "customer"
    BUSINESS = "business"
    TYPE_CHOICES = [(CUSTOMER, "Customer"), (BUSINESS, "Business")]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    location = models.CharField(max_length=100, blank=True, default="")
    file = models.FileField(upload_to="user_files/", blank=True, null=True)
    tel = models.CharField(max_length=20, blank=True, default="")
    description = models.TextField(blank=True, default="")
    working_hours = models.CharField(max_length=200, blank=True, default="")
    type = models.CharField(max_length=20, choices=TYPE_CHOICES, default=CUSTOMER)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "User Profile"
        verbose_name_plural = "User Profiles"
        ordering = ["created_at"]

    def __str__(self):
        return f"{self.user.username} ({self.type})"
