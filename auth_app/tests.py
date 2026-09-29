"""Tests for registration and login."""

from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.test import APITestCase

from auth_app.models import UserProfile


def registration_data():
    """Return a valid customer registration payload."""
    return {
        "username": "newuser",
        "email": "new@coderr.de",
        "password": "coderr26",
        "repeated_password": "coderr26",
        "type": "customer",
    }


class RegistrationTests(APITestCase):
    """Tests for POST /api/registration/."""

    url = "/api/registration/"

    def test_creates_customer_and_returns_token(self):
        """A valid registration returns 201 and creates a profile."""
        response = self.client.post(self.url, registration_data(), format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["username"], "newuser")
        self.assertIn("token", response.data)
        user = User.objects.get(username="newuser")
        self.assertEqual(user.profile.type, UserProfile.CUSTOMER)

    def test_rejects_mismatched_passwords(self):
        """Different password fields return 400."""
        data = registration_data()
        data["repeated_password"] = "otherpass1"
        response = self.client.post(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(User.objects.filter(username="newuser").exists())


class LoginTests(APITestCase):
    """Tests for POST /api/login/."""

    url = "/api/login/"

    def setUp(self):
        """Create one customer that the login tests can use."""
        user = User.objects.create_user(
            username="Mike",
            email="mike@coderr.de",
            password="coderr26",
        )
        UserProfile.objects.create(user=user, type=UserProfile.CUSTOMER)

    def test_returns_token_for_valid_credentials(self):
        """A correct password returns 200 and a token."""
        response = self.client.post(
            self.url,
            {"username": "Mike", "password": "coderr26"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["username"], "Mike")
        self.assertIn("token", response.data)

    def test_rejects_wrong_password(self):
        """A wrong password returns 400."""
        response = self.client.post(
            self.url,
            {"username": "Mike", "password": "wrongpass1"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class ProfileTests(APITestCase):
    """Tests for the profile detail and list endpoints."""

    def setUp(self):
        """Create one customer and one business user, both with tokens."""
        self.mike = User.objects.create_user(
            username="Mike", email="mike@coderr.de", password="coderr26"
        )
        UserProfile.objects.create(user=self.mike, type=UserProfile.CUSTOMER)
        self.anthony = User.objects.create_user(
            username="Anthony", email="anthony@coderr.de", password="coderr26"
        )
        UserProfile.objects.create(user=self.anthony, type=UserProfile.BUSINESS)

    def login(self, user):
        """Send the user's token on later requests."""
        token, _ = Token.objects.get_or_create(user=user)
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {token.key}")

    def test_owner_can_read_and_update_profile(self):
        """GET returns the user id, PATCH writes the first name."""
        self.login(self.mike)
        url = f"/api/profile/{self.mike.id}/"
        read_response = self.client.get(url)
        self.assertEqual(read_response.status_code, status.HTTP_200_OK)
        self.assertEqual(read_response.data["user"], self.mike.id)
        self.assertEqual(read_response.data["location"], "")
        patch_response = self.client.patch(url, {"first_name": "Mike"}, format="json")
        self.assertEqual(patch_response.status_code, status.HTTP_200_OK)
        self.mike.refresh_from_db()
        self.assertEqual(self.mike.first_name, "Mike")

    def test_other_user_cannot_patch_profile(self):
        """A business user gets 403 when editing a customer profile."""
        self.login(self.anthony)
        response = self.client.patch(
            f"/api/profile/{self.mike.id}/",
            {"location": "Berlin"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_profile_list_requires_authentication(self):
        """The business list is 401 without a token and 200 with one."""
        anonymous = self.client.get("/api/profiles/business/")
        self.assertEqual(anonymous.status_code, status.HTTP_401_UNAUTHORIZED)
        self.login(self.mike)
        authenticated = self.client.get("/api/profiles/business/")
        self.assertEqual(authenticated.status_code, status.HTTP_200_OK)
        self.assertEqual(len(authenticated.data), 1)
        self.assertEqual(authenticated.data[0]["username"], "Anthony")
