"""Views for business reviews."""

from rest_framework import viewsets
from rest_framework.filters import OrderingFilter
from rest_framework.permissions import IsAuthenticated

from orders_app.api.permissions import IsCustomerUser
from reviews_app.api.permissions import IsReviewer
from reviews_app.api.serializers import ReviewSerializer
from reviews_app.models import Review


def apply_review_filters(queryset, params):
    """Filter reviews by business user or reviewer."""
    business_user_id = params.get("business_user_id")
    if business_user_id:
        queryset = queryset.filter(business_user_id=business_user_id)
    reviewer_id = params.get("reviewer_id")
    if reviewer_id:
        queryset = queryset.filter(reviewer_id=reviewer_id)
    return queryset


class ReviewViewSet(viewsets.ModelViewSet):
    """Handles list, create, update and delete for reviews.

    Backs ``/api/reviews/`` and ``/api/reviews/{id}/``.
    """

    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    http_method_names = ["get", "post", "patch", "delete", "head", "options"]
    filter_backends = [OrderingFilter]
    ordering_fields = ["updated_at", "rating"]

    def get_permissions(self):
        """Return permission instances for the current action."""
        if self.action == "create":
            return [IsAuthenticated(), IsCustomerUser()]
        if self.action in ("partial_update", "destroy"):
            return [IsAuthenticated(), IsReviewer()]
        return [IsAuthenticated()]

    def get_queryset(self):
        """Return reviews matching the query parameters."""
        queryset = super().get_queryset().select_related("business_user", "reviewer")
        return apply_review_filters(queryset, self.request.query_params)

    def perform_create(self, serializer):
        """Store the logged-in user as the reviewer."""
        serializer.save(reviewer=self.request.user)
