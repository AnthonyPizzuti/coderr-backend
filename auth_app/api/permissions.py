"""Custom permissions for the auth app."""

from rest_framework.permissions import SAFE_METHODS, BasePermission


class IsOwnerOrReadOnly(BasePermission):
    """Allows read access to everyone and write access to the owner only."""

    def has_object_permission(self, request, view, obj):
        """Return whether the request may act on this profile."""

        if request.method in SAFE_METHODS:
            return True
        return obj.user == request.user
