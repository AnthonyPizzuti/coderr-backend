"""URL routes for the offers API."""

from django.urls import path

from offers_app.api.views import OfferDetailRetrieveView, OfferViewSet

urlpatterns = [
    path(
        "offers/",
        OfferViewSet.as_view({"get": "list", "post": "create"}),
        name="offer-list",
    ),
    path(
        "offers/<int:pk>/",
        OfferViewSet.as_view(
            {"get": "retrieve", "patch": "partial_update", "delete": "destroy"}
        ),
        name="offer-detail",
    ),
    path(
        "offerdetails/<int:pk>/",
        OfferDetailRetrieveView.as_view(),
        name="offerdetail-detail",
    ),
]
