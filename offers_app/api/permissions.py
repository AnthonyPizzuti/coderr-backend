"""Custom permissions for the offers app."""

from rest_framework import permissions

from auth_app.models import UserProfile


class IsBusinessUser(permissions.BasePermission):
    """Allows access only to authenticated users with a business profile."""

    def has_permission(self, request, view):
        """Return whether the requesting user may create offers."""
        user = request.user
        return (
            user.is_authenticated
            and hasattr(user, "profile")
            and user.profile.type == UserProfile.BUSINESS
        )
