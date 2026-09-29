"""Views for customer orders."""

from django.db.models import Q
from rest_framework import viewsets
from rest_framework.permissions import IsAdminUser, IsAuthenticated

from orders_app.api.permissions import IsCustomerUser, IsOrderBusinessUser
from orders_app.api.serializers import OrderCreateSerializer, OrderSerializer
from orders_app.models import Order


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
