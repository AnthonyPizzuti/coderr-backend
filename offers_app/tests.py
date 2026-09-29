"""Tests for offer list, create and permissions."""

from decimal import Decimal

from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.test import APITestCase

from auth_app.models import UserProfile


def make_user(username, account_type):
    """Create a user with a profile and return both."""
    user = User.objects.create_user(
        username=username,
        email=f"{username}@coderr.de",
        password="coderr26",
    )
    UserProfile.objects.create(user=user, type=account_type)
    return user


def detail_payload(offer_type, price):
    """Return one offer-detail body for the given package type."""
    return {
        "title": offer_type,
        "revisions": 2,
        "delivery_time_in_days": 5,
        "price": price,
        "features": ["Logo"],
        "offer_type": offer_type,
    }


class OfferTests(APITestCase):
    """Tests for /api/offers/."""

    url = "/api/offers/"

    def setUp(self):
        """Create one customer and one business user."""
        self.mike = make_user("Mike", UserProfile.CUSTOMER)
        self.anthony = make_user("Anthony", UserProfile.BUSINESS)

    def login(self, user):
        """Send the user's token on later requests."""
        token, _ = Token.objects.get_or_create(user=user)
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {token.key}")

    def offer_body(self):
        """Return a valid offer with basic, standard and premium."""
        return {
            "title": "Logo Paket",
            "description": "Drei Pakete",
            "details": [
                detail_payload("basic", 100),
                detail_payload("standard", 200),
                detail_payload("premium", 500),
            ],
        }

    def test_business_user_can_create_offer(self):
        """POST returns 201 and the public list shows the minimum price."""
        self.login(self.anthony)
        created = self.client.post(self.url, self.offer_body(), format="json")
        self.assertEqual(created.status_code, status.HTTP_201_CREATED)
        self.assertEqual(len(created.data["details"]), 3)
        self.client.credentials()
        listed = self.client.get(self.url)
        self.assertEqual(listed.status_code, status.HTTP_200_OK)
        self.assertEqual(listed.data["count"], 1)
        result = listed.data["results"][0]
        self.assertEqual(result["min_price"], Decimal("100"))
        self.assertIn("/api/offerdetails/", result["details"][0]["url"])

    def test_customer_cannot_create_offer(self):
        """A customer account receives 403."""
        self.login(self.mike)
        response = self.client.post(self.url, self.offer_body(), format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_offer_requires_three_detail_types(self):
        """A single detail package returns 400."""
        self.login(self.anthony)
        body = self.offer_body()
        body["details"] = body["details"][:1]
        response = self.client.post(self.url, body, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_only_owner_can_update_offer(self):
        """The customer gets 403, and a guest cannot open the detail."""
        self.login(self.anthony)
        created = self.client.post(self.url, self.offer_body(), format="json")
        offer_id = created.data["id"]
        self.login(self.mike)
        forbidden = self.client.patch(
            f"{self.url}{offer_id}/",
            {"title": "Geklaut"},
            format="json",
        )
        self.assertEqual(forbidden.status_code, status.HTTP_403_FORBIDDEN)
        self.client.credentials()
        anonymous = self.client.get(f"{self.url}{offer_id}/")
        self.assertEqual(anonymous.status_code, status.HTTP_401_UNAUTHORIZED)
