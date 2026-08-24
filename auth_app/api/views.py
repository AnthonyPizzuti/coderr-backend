from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from auth_app.api.serializers import LoginSerializer, RegistrationSerializer


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
