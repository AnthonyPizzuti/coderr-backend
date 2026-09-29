"""Tests for the public platform statistics."""

from rest_framework import status
from rest_framework.test import APITestCase

from auth_app.models import UserProfile
from django.contrib.auth.models import User
from offers_app.models import Offer


class BaseInfoTests(APITestCase):
    """Tests for GET /api/base-info/."""

    def test_counts_are_public(self):
        """Guests receive the four statistics without a token."""
        user = User.objects.create_user(username="Anthony", password="coderr26")
        UserProfile.objects.create(user=user, type=UserProfile.BUSINESS)
        Offer.objects.create(user=user, title="Logo", description="Text")
        response = self.client.get("/api/base-info/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["review_count"], 0)
        self.assertEqual(response.data["average_rating"], 0.0)
        self.assertEqual(response.data["business_profile_count"], 1)
        self.assertEqual(response.data["offer_count"], 1)
