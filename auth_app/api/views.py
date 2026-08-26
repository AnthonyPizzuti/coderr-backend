"""Views for registration, authentication and user profiles."""

from rest_framework import generics, status
from rest_framework.authtoken.models import Token
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from auth_app.api.permissions import IsOwnerOrReadOnly
from auth_app.api.serializers import (
    BusinessProfileSerializer,
    CustomerProfileSerializer,
    LoginSerializer,
    RegistrationSerializer,
    ProfileSerializer,
)
from auth_app.models import UserProfile


class RegistrationView(APIView):
    """Handles user registration.

    Backs ``POST /api/registration/``.
    """

    permission_classes = [AllowAny]

    def post(self, request):
        """Create a new user and return the auth token."""
        serializer = RegistrationSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            token, _ = Token.objects.get_or_create(user=user)
            return Response(
                {
                    "token": token.key,
                    "username": user.username,
                    "email": user.email,
                    "user_id": user.id,
                },
                status=status.HTTP_201_CREATED,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LoginView(APIView):
    """Handles user login.

    Backs ``POST /api/login/``.
    """

    permission_classes = [AllowAny]

    def post(self, request):
        """Authenticate the user and return the auth token."""
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data["user"]
            token, _ = Token.objects.get_or_create(user=user)
            return Response(
                {
                    "token": token.key,
                    "username": user.username,
                    "email": user.email,
                    "user_id": user.id,
                },
                status=status.HTTP_200_OK,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ProfileDetailView(generics.RetrieveUpdateAPIView):
    """Returns and updates a single user profile.

    Backs ``GET`` and ``PATCH`` on ``/api/profile/{pk}/``. The URL
    parameter is the id of the user, not the profile's own primary key.
    """

    queryset = UserProfile.objects.select_related("user")
    serializer_class = ProfileSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrReadOnly]
    lookup_field = "user_id"
    lookup_url_kwarg = "pk"
    http_method_names = ["get", "patch", "options", "head"]


class BusinessProfileListView(generics.ListAPIView):
    """Returns a list of all business profiles.

    Backs ``GET /api/profiles/business/``.
    """

    queryset = UserProfile.objects.filter(type=UserProfile.BUSINESS).select_related(
        "user"
    )
    serializer_class = BusinessProfileSerializer


class CustomerProfileListView(generics.ListAPIView):
    """Returns a list of all customer profiles.

    Backs ``GET /api/profiles/customer/``.
    """

    queryset = UserProfile.objects.filter(type=UserProfile.CUSTOMER).select_related(
        "user"
    )
    serializer_class = CustomerProfileSerializer
