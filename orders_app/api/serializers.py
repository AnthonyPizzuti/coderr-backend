"""Serializers for customer orders."""

from django.shortcuts import get_object_or_404
from rest_framework import serializers

from offers_app.models import OfferDetail
from orders_app.models import Order


class OrderSerializer(serializers.ModelSerializer):
    """Serializes an order for list, retrieve and status updates.

    Backs ``GET /api/orders/`` and ``PATCH /api/orders/{id}/``.
    Only ``status`` may be written.
    """

    class Meta:
        model = Order
        fields = [
            "id",
            "customer_user",
            "business_user",
            "title",
            "revisions",
            "delivery_time_in_days",
            "price",
            "features",
            "offer_type",
            "status",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "customer_user",
            "business_user",
            "title",
            "revisions",
            "delivery_time_in_days",
            "price",
            "features",
            "offer_type",
            "created_at",
            "updated_at",
        ]


def build_order(detail, customer):
    """Copy an offer detail into a new in-progress order."""
    return Order.objects.create(
        customer_user=customer,
        business_user=detail.offer.user,
        title=detail.title,
        revisions=detail.revisions,
        delivery_time_in_days=detail.delivery_time_in_days,
        price=detail.price,
        features=list(detail.features),
        offer_type=detail.offer_type,
    )


class OrderCreateSerializer(serializers.Serializer):
    """Creates an order from an offer detail id.

    Backs ``POST /api/orders/``. The body contains only
    ``offer_detail_id``.
    """

    offer_detail_id = serializers.IntegerField()

    def create(self, validated_data):
        """Load the detail and store a snapshot as a new order."""
        detail = get_object_or_404(
            OfferDetail.objects.select_related("offer"),
            pk=validated_data["offer_detail_id"],
        )
        return build_order(detail, self.context["request"].user)

    def to_representation(self, instance):
        """Return the new order in the same shape as ``OrderSerializer``."""
        return OrderSerializer(instance).data
