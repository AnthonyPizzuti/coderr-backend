"""Serializers for offers and offer details."""

from django.contrib.auth.models import User
from rest_framework import serializers

from offers_app.models import Offer, OfferDetail


class OfferDetailSerializer(serializers.ModelSerializer):
    """Serializes a full offer detail.

    Backs ``GET /api/offerdetails/{id}/`` and the nested ``details``
    payload of POST and PATCH on ``/api/offers/``.
    """

    class Meta:
        model = OfferDetail
        fields = [
            "id",
            "title",
            "revisions",
            "delivery_time_in_days",
            "price",
            "features",
            "offer_type",
        ]


class OfferDetailLinkSerializer(serializers.ModelSerializer):
    """Serializes an offer detail as id and URL only.

    Used in the ``details`` list of GET ``/api/offers/`` and
    GET ``/api/offers/{id}/``.
    """

    url = serializers.HyperlinkedIdentityField(view_name="offerdetail-detail")

    class Meta:
        model = OfferDetail
        fields = ["id", "url"]


class UserDetailsSerializer(serializers.ModelSerializer):
    """Serializes the public name fields of an offer's creator."""

    class Meta:
        model = User
        fields = ["first_name", "last_name", "username"]


class OfferListSerializer(serializers.ModelSerializer):
    """Serializes an offer for the paginated list endpoint.

    Backs ``GET /api/offers/``. ``min_price`` and ``min_delivery_time``
    are read from queryset annotations, not computed here.
    """

    details = OfferDetailLinkSerializer(many=True, read_only=True)
    min_price = serializers.DecimalField(
        max_digits=10, decimal_places=2, read_only=True, allow_null=True
    )
    min_delivery_time = serializers.IntegerField(read_only=True, allow_null=True)
    user_details = UserDetailsSerializer(source="user", read_only=True)

    class Meta:
        model = Offer
        fields = [
            "id",
            "user",
            "title",
            "image",
            "description",
            "created_at",
            "updated_at",
            "details",
            "min_price",
            "min_delivery_time",
            "user_details",
        ]
        extra_kwargs = {"user": {"read_only": True}}


class OfferRetrieveSerializer(OfferListSerializer):
    """Serializes a single offer.

    Backs ``GET /api/offers/{id}/``. Same shape as the list item, but
    without ``user_details``.
    """

    class Meta(OfferListSerializer.Meta):
        fields = [
            "id",
            "user",
            "title",
            "image",
            "description",
            "created_at",
            "updated_at",
            "details",
            "min_price",
            "min_delivery_time",
        ]


def _create_details(offer, details_data):
    """Create all nested detail rows for a newly saved offer."""
    for item in details_data:
        OfferDetail.objects.create(offer=offer, **item)


def _update_details(offer, details_data):
    """Patch existing details, identified by ``offer_type``."""
    for item in details_data:
        offer_type = item.pop("offer_type", None)
        if not offer_type:
            raise serializers.ValidationError("Each detail needs an offer_type.")
        detail = offer.details.filter(offer_type=offer_type).first()
        if detail is None:
            raise serializers.ValidationError("Unknown offer_type.")
        for attr, value in item.items():
            setattr(detail, attr, value)
        detail.save()


def collect_detail_types(details):
    """Return the offer types, rejecting entries without one."""
    types = []
    for item in details:
        offer_type = item.get("offer_type")
        if not offer_type:
            raise serializers.ValidationError("Each detail needs an offer_type.")
        types.append(offer_type)
    return types


class OfferWriteSerializer(serializers.ModelSerializer):
    """Creates and updates an offer together with its details.

    Backs ``POST /api/offers/`` and ``PATCH /api/offers/{id}/``.
    """

    details = OfferDetailSerializer(many=True)

    class Meta:
        model = Offer
        fields = ["id", "title", "image", "description", "details"]

    def validate_details(self, value):
        """Require three unique types on create; unique types on update."""
        types = collect_detail_types(value)
        valid = {OfferDetail.BASIC, OfferDetail.STANDARD, OfferDetail.PREMIUM}
        if len(types) != len(set(types)):
            raise serializers.ValidationError("Each offer_type may appear only once.")
        if not self.instance and set(types) != valid:
            raise serializers.ValidationError(
                "An offer must contain exactly one basic, standard and premium detail."
            )
        return value

    def create(self, validated_data):
        """Create the offer for the requesting user, then its details."""
        details_data = validated_data.pop("details")
        offer = Offer.objects.create(
            user=self.context["request"].user, **validated_data
        )
        _create_details(offer, details_data)
        return offer

    def update(self, instance, validated_data):
        """Update offer fields; patch details when they are present."""
        details_data = validated_data.pop("details", None)
        instance = super().update(instance, validated_data)
        if details_data:
            _update_details(instance, details_data)
        return instance
