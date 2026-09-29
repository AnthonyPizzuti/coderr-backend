"""Custom permissions for the reviews app."""

from rest_framework.permissions import BasePermission


class IsReviewer(BasePermission):
    """Allows changes only to the user who wrote the review."""

    def has_object_permission(self, request, view, obj):
        """Return whether this user wrote the review."""
        return obj.reviewer_id == request.user.id
