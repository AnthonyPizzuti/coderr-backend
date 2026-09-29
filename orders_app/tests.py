"""Tests for creating orders and updating their status."""

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


def offer_body():
    """Return an offer with three package types."""
    details = []
    for offer_type, price in (("basic", 100), ("standard", 200), ("premium", 500)):
        details.append(
            {
                "title": offer_type,
                "revisions": 2,
                "delivery_time_in_days": 5,
                "price": price,
                "features": ["Logo"],
                "offer_type": offer_type,
            }
        )
    return {"title": "Logo Paket", "description": "Drei Pakete", "details": details}


class OrderTests(APITestCase):
    """Tests for /api/orders/ and the count endpoints."""

    def setUp(self):
        """Create a customer, a business user and one offer."""
        self.mike = make_user("Mike", UserProfile.CUSTOMER)
        self.anthony = make_user("Anthony", UserProfile.BUSINESS)
        self.login(self.anthony)
        created = self.client.post("/api/offers/", offer_body(), format="json")
        self.detail_id = created.data["details"][0]["id"]
        self.client.credentials()

    def login(self, user):
        """Send the user's token on later requests."""
        token, _ = Token.objects.get_or_create(user=user)
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {token.key}")

    def test_customer_can_create_order(self):
        """POST copies the detail onto a new in-progress order."""
        self.login(self.mike)
        created = self.client.post(
            "/api/orders/",
            {"offer_detail_id": self.detail_id},
            format="json",
        )
        self.assertEqual(created.status_code, status.HTTP_201_CREATED)
        self.assertEqual(created.data["status"], "in_progress")
        self.assertEqual(created.data["customer_user"], self.mike.id)
        self.assertEqual(created.data["business_user"], self.anthony.id)

    def test_business_can_complete_an_order(self):
        """The business user sets the status and the counter follows."""
        self.login(self.mike)
        created = self.client.post(
            "/api/orders/",
            {"offer_detail_id": self.detail_id},
            format="json",
        )
        self.login(self.anthony)
        order_url = f"/api/orders/{created.data['id']}/"
        patched = self.client.patch(order_url, {"status": "completed"}, format="json")
        self.assertEqual(patched.status_code, status.HTTP_200_OK)
        count = self.client.get(f"/api/completed-order-count/{self.anthony.id}/")
        self.assertEqual(count.data["completed_order_count"], 1)

    def test_business_user_cannot_create_an_order(self):
        """Only a customer may post an order."""
        self.login(self.anthony)
        response = self.client.post(
            "/api/orders/",
            {"offer_detail_id": self.detail_id},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_unknown_business_user_count_is_404(self):
        """A customer id is not a valid business user for the counter."""
        self.login(self.mike)
        response = self.client.get(f"/api/order-count/{self.mike.id}/")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
