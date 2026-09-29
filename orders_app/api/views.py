"""Views for customer orders."""

from django.db.models import Q
from rest_framework import viewsets
from rest_framework.permissions import IsAdminUser, IsAuthenticated

from orders_app.api.permissions import IsCustomerUser, IsOrderBusinessUser
from orders_app.api.serializers import OrderCreateSerializer, OrderSerializer
from orders_app.models import Order

from django.http import Http404
from rest_framework.response import Response
from rest_framework.views import APIView

from auth_app.models import UserProfile
from django.contrib.auth.models import User


class OrderViewSet(viewsets.ModelViewSet):
    """Handles list, create, status update and delete for orders.

    Backs ``/api/orders/`` and ``/api/orders/{id}/``.
    """

    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    http_method_names = ["get", "post", "patch", "delete", "head", "options"]

    def get_serializer_class(self):
        """Use the create serializer only for POST."""
        if self.action == "create":
            return OrderCreateSerializer
        return OrderSerializer

    def get_permissions(self):
        """Return permission instances for the current action."""
        if self.action == "create":
            return [IsAuthenticated(), IsCustomerUser()]
        if self.action == "partial_update":
            return [IsAuthenticated(), IsOrderBusinessUser()]
        if self.action == "destroy":
            return [IsAuthenticated(), IsAdminUser()]
        return [IsAuthenticated()]

    def get_queryset(self):
        """Limit the list to orders the user is part of.

        Staff may delete any order, so destroy keeps the full queryset.
        """
        queryset = (
            super().get_queryset().select_related("customer_user", "business_user")
        )
        if self.action == "destroy":
            return queryset
        user = self.request.user
        return queryset.filter(Q(customer_user=user) | Q(business_user=user))


class OrderCountView(APIView):
    """Counts orders of one business user in a single status.

    Backs ``GET /api/order-count/{business_user_id}/``.
    """

    permission_classes = [IsAuthenticated]
    order_status = Order.Status.IN_PROGRESS
    response_key = "order_count"

    def get(self, request, business_user_id):
        """Return the count, or 404 if that user is not a business profile."""
        business_exists = User.objects.filter(
            pk=business_user_id,
            profile__type=UserProfile.BUSINESS,
        ).exists()
        if not business_exists:
            raise Http404
        count = Order.objects.filter(
            business_user_id=business_user_id,
            status=self.order_status,
        ).count()
        return Response({self.response_key: count})


class CompletedOrderCountView(OrderCountView):
    """Counts completed orders of one business user.

    Backs ``GET /api/completed-order-count/{business_user_id}/``.
    """

    order_status = Order.Status.COMPLETED
    response_key = "completed_order_count"
