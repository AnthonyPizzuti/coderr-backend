"""URL routes for the reviews API."""

from django.urls import path

from reviews_app.api.views import ReviewViewSet

urlpatterns = [
    path(
        "reviews/",
        ReviewViewSet.as_view({"get": "list", "post": "create"}),
        name="review-list",
    ),
    path(
        "reviews/<int:pk>/",
        ReviewViewSet.as_view({"patch": "partial_update", "delete": "destroy"}),
        name="review-detail",
    ),
]
