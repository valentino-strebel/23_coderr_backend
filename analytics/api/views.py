from django.contrib.auth import get_user_model
from django.db.models import Avg
from rest_framework import generics, status
from rest_framework.response import Response

from reviews.models import Review
from offers.models import Offer


class BaseInfoView(generics.GenericAPIView):
    """
    GET /api/base-info/
    - No authentication required
    - Returns:
        review_count: total number of reviews
        average_rating: average rating across all reviews, rounded to 1 decimal
        business_profile_count: number of users with type='business'
        offer_count: total number of offers
    """
    authentication_classes = []  # No auth required
    permission_classes = []      # Public endpoint

    def get(self, request):
        User = get_user_model()

        # Count reviews
        review_count = Review.objects.count()

        # Average rating (rounded to 1 decimal place)
        avg_rating = Review.objects.aggregate(avg=Avg("rating"))["avg"]
        average_rating = round(avg_rating, 1) if avg_rating is not None else 0.0

        # Count business profiles
        # Adjust logic depending on where you store the "business" flag
        business_profile_count = User.objects.filter(user_type="business").count()
        # Or, if using profile relation:
        # business_profile_count = User.objects.filter(profile__type="business").count()

        # Count offers
        offer_count = Offer.objects.count()

        data = {
            "review_count": review_count,
            "average_rating": average_rating,
            "business_profile_count": business_profile_count,
            "offer_count": offer_count,
        }
        return Response(data, status=status.HTTP_200_OK)
