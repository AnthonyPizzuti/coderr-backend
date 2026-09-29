"""Views for platform-wide statistics."""

from django.db.models import Avg
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from auth_app.models import UserProfile
from offers_app.models import Offer
from reviews_app.models import Review


class BaseInfoView(APIView):
    """Returns platform statistics.

    Backs ``GET /api/base-info/``.
    """

    permission_classes = [AllowAny]

    def get(self, request):
        """Return review, business and offer counts."""
        average = Review.objects.aggregate(value=Avg("rating"))["value"]
        if average is None:
            average = 0
        return Response(
            {
                "review_count": Review.objects.count(),
                "average_rating": round(average, 1),
                "business_profile_count": UserProfile.objects.filter(
                    type=UserProfile.BUSINESS
                ).count(),
                "offer_count": Offer.objects.count(),
            }
        )
