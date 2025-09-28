from django.contrib.auth import get_user_model
from django.db.models import Avg
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.renderers import JSONRenderer

from reviews.models import Review
from offers.models import Offer


class BaseInfoView(generics.GenericAPIView):
    """
    @endpoint
    @name Base Info
    @route GET /api/base-info/
    @auth None (public endpoint)
    @description
        Provides general statistics about reviews, ratings, business profiles, and offers.

    @returns {Object} 200 - Success response
    @returns {number} review_count - Total number of reviews
    @returns {float} average_rating - Average rating across all reviews (rounded to 1 decimal)
    @returns {number} business_profile_count - Number of users with user_type="business"
    @returns {number} offer_count - Total number of offers

    @example
    # Request:
    GET /api/base-info/

    # Response 200:
    {
        "review_count": 128,
        "average_rating": 4.3,
        "business_profile_count": 52,
        "offer_count": 89
    }
    """

    authentication_classes = []
    permission_classes = []
    renderer_classes = [JSONRenderer]

    def get(self, request):
        User = get_user_model()

        review_count = Review.objects.count()
        avg_rating = Review.objects.aggregate(avg=Avg("rating"))["avg"]
        average_rating = round(avg_rating, 1) if avg_rating is not None else 0.0
        business_profile_count = User.objects.filter(user_type="business").count()
        offer_count = Offer.objects.count()

        data = {
            "review_count": review_count,
            "average_rating": average_rating,
            "business_profile_count": business_profile_count,
            "offer_count": offer_count,
        }
        return Response(data, status=status.HTTP_200_OK)
