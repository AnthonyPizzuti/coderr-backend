"""Custom permissions for the orders app."""

from rest_framework.permissions import BasePermission

from auth_app.models import UserProfile


class IsCustomerUser(BasePermission):
    """Allows access only to authenticated users with a customer profile."""

    def has_permission(self, request, view):
        """Return whether the requesting user may place an order."""
        user = request.user
        return (
            user.is_authenticated
            and hasattr(user, "profile")
            and user.profile.type == UserProfile.CUSTOMER
        )


class IsOrderBusinessUser(BasePermission):
    """Allows a status change only to the order's business user."""

    def has_object_permission(self, request, view, obj):
        """Return whether this user may update this order."""
        user = request.user
        return (
            hasattr(user, "profile")
            and user.profile.type == UserProfile.BUSINESS
            and obj.business_user_id == user.id
        )
