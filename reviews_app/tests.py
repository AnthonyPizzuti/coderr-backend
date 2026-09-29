"""Tests for creating and updating reviews."""

from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.test import APITestCase

from auth_app.models import UserProfile


def make_user(username, account_type):
    """Create a user with a profile."""
    user = User.objects.create_user(
        username=username,
        email=f"{username}@coderr.de",
        password="coderr26",
    )
    UserProfile.objects.create(user=user, type=account_type)
    return user


class ReviewTests(APITestCase):
    """Tests for /api/reviews/."""

    url = "/api/reviews/"

    def setUp(self):
        """Create a customer and a business user."""
        self.mike = make_user("Mike", UserProfile.CUSTOMER)
        self.anthony = make_user("Anthony", UserProfile.BUSINESS)

    def login(self, user):
        """Send the user's token on later requests."""
        token, _ = Token.objects.get_or_create(user=user)
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {token.key}")

    def review_body(self):
        """Return a valid review payload for Anthony."""
        return {
            "business_user": self.anthony.id,
            "rating": 5,
            "description": "Sehr gut",
        }

    def test_customer_can_review_a_business_once(self):
        """The first review is 201, the second one for the same business is 400."""
        self.login(self.mike)
        created = self.client.post(self.url, self.review_body(), format="json")
        self.assertEqual(created.status_code, status.HTTP_201_CREATED)
        self.assertEqual(created.data["reviewer"], self.mike.id)
        self.assertEqual(created.data["rating"], 5)
        duplicate = self.client.post(self.url, self.review_body(), format="json")
        self.assertEqual(duplicate.status_code, status.HTTP_400_BAD_REQUEST)

    def test_only_the_author_can_update(self):
        """Anthony cannot change Mike's rating."""
        self.login(self.mike)
        created = self.client.post(self.url, self.review_body(), format="json")
        self.login(self.anthony)
        response = self.client.patch(
            f"{self.url}{created.data['id']}/",
            {"rating": 1},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_list_filters_by_business_user(self):
        """The profile page query returns only that business user's reviews."""
        self.login(self.mike)
        self.client.post(self.url, self.review_body(), format="json")
        listed = self.client.get(
            f"{self.url}?business_user_id={self.anthony.id}&ordering=-updated_at"
        )
        self.assertEqual(listed.status_code, status.HTTP_200_OK)
        self.assertEqual(len(listed.data), 1)
        self.assertEqual(listed.data[0]["business_user"], self.anthony.id)
