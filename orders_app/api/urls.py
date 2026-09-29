"""URL routes for the orders API."""

from django.urls import path

from orders_app.api.views import OrderViewSet

urlpatterns = [
    path(
        "orders/",
        OrderViewSet.as_view({"get": "list", "post": "create"}),
        name="order-list",
    ),
    path(
        "orders/<int:pk>/",
        OrderViewSet.as_view(
            {
                "get": "retrieve",
                "patch": "partial_update",
                "delete": "destroy",
            }
        ),
        name="order-detail",
    ),
]
