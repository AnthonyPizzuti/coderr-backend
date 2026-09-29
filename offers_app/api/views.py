"""Views for offers and offer details."""

from django.db.models import Min
from rest_framework import generics, viewsets
from rest_framework.exceptions import ValidationError
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import AllowAny, IsAuthenticated

from auth_app.api.permissions import IsOwnerOrReadOnly
from offers_app.api.permissions import IsBusinessUser
from offers_app.api.serializers import (
    OfferDetailSerializer,
    OfferListSerializer,
    OfferRetrieveSerializer,
    OfferWriteSerializer,
)
from offers_app.models import Offer, OfferDetail


def as_number(value):
    """Return a query value as a number, or raise 400."""
    try:
        return float(value)
    except (TypeError, ValueError):
        raise ValidationError("A valid number is required.")


def apply_offer_filters(queryset, params):
    """Apply creator, price and delivery-time query filters."""
    creator_id = params.get("creator_id")
    if creator_id:
        queryset = queryset.filter(user_id=as_number(creator_id))
    min_price = params.get("min_price")
    if min_price:
        queryset = queryset.filter(min_price__gte=as_number(min_price))
    max_delivery_time = params.get("max_delivery_time")
    if max_delivery_time:
        queryset = queryset.filter(min_delivery_time__lte=as_number(max_delivery_time))
    return queryset


class OfferPagination(PageNumberPagination):
    """Page-number pagination with a default size of 6.

    The client may override the size via ``?page_size=``.
    """

    page_size = 6
    page_size_query_param = "page_size"


class OfferViewSet(viewsets.ModelViewSet):
    """Handles list, create, retrieve, update and delete for offers.

    Backs ``/api/offers/`` and ``/api/offers/{id}/``.
    """

    queryset = Offer.objects.all()
    serializer_class = OfferListSerializer
    http_method_names = ["get", "post", "patch", "delete", "head", "options"]
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ["title", "description"]
    ordering_fields = ["updated_at", "min_price"]
    pagination_class = OfferPagination

    def get_serializer_class(self):
        """Return the serializer that matches the current action."""
        if self.action == "list":
            return OfferListSerializer
        if self.action == "retrieve":
            return OfferRetrieveSerializer
        return OfferWriteSerializer

    def get_permissions(self):
        """Return permission instances for the current action."""
        if self.action == "list":
            return [AllowAny()]
        if self.action == "create":
            return [IsAuthenticated(), IsBusinessUser()]
        if self.action in ("partial_update", "destroy"):
            return [IsAuthenticated(), IsOwnerOrReadOnly()]
        return [IsAuthenticated()]

    def get_queryset(self):
        """Return offers annotated with min price and delivery time."""
        queryset = (
            super()
            .get_queryset()
            .select_related("user")
            .prefetch_related("details")
            .annotate(
                min_price=Min("details__price"),
                min_delivery_time=Min("details__delivery_time_in_days"),
            )
        )
        return apply_offer_filters(queryset, self.request.query_params).order_by(
            "-updated_at"
        )


class OfferDetailRetrieveView(generics.RetrieveAPIView):
    """Returns a single offer detail.

    Backs ``GET /api/offerdetails/{id}/``.
    """

    queryset = OfferDetail.objects.all()
    serializer_class = OfferDetailSerializer
    permission_classes = [IsAuthenticated]
