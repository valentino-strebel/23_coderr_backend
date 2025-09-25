"""
@file views.py
@description
    Provides endpoints for creating, listing, updating, and deleting reviews.
"""

from rest_framework import generics, parsers, permissions, filters

from reviews.models import Review
from .serializers import ReviewCreateSerializer, ReviewSerializer, ReviewUpdateSerializer
from core.permissions import IsCustomerUser, IsReviewOwner


class ReviewListCreateView(generics.ListCreateAPIView):
    """
    @endpoint ReviewListCreateView
    @route GET /api/reviews/
    @route POST /api/reviews/
    @auth
        GET  - Authenticated users
        POST - Authenticated users of type "customer"
    @description
        - GET: Returns a list of reviews, optionally filtered and ordered.
        - POST: Creates a new review for a business user.
    @query_params
        business_user_id {int} - Filter reviews by business user
        reviewer_id {int} - Filter reviews by reviewer
        ordering {string} - Order by "updated_at", "-updated_at", "rating", "-rating"
    """
    queryset = Review.objects.all()
    parser_classes = [parsers.JSONParser]
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ["updated_at", "rating"]
    ordering = ["-updated_at"]

    def get_permissions(self):
        if self.request.method.upper() == "POST":
            return [permissions.IsAuthenticated(), IsCustomerUser()]
        return [permissions.IsAuthenticated()]

    def get_serializer_class(self):
        if self.request.method.upper() == "POST":
            return ReviewCreateSerializer
        return ReviewSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        business_user_id = self.request.query_params.get("business_user_id")
        reviewer_id = self.request.query_params.get("reviewer_id")

        if business_user_id:
            qs = qs.filter(business_user_id=business_user_id)
        if reviewer_id:
            qs = qs.filter(reviewer_id=reviewer_id)
        return qs


class ReviewUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    """
    @endpoint ReviewUpdateDestroyView
    @route PATCH /api/reviews/<id>/
    @route DELETE /api/reviews/<id>/
    @auth Authenticated users; only review owners may update or delete
    @description
        - PATCH: Allows a review author to update "rating" and "description".
        - DELETE: Allows a review author to delete the review.
    """
    queryset = Review.objects.all()
    serializer_class = ReviewUpdateSerializer
    permission_classes = [permissions.IsAuthenticated, IsReviewOwner]
    parser_classes = [parsers.JSONParser]
    lookup_field = "pk"
    http_method_names = ["patch", "delete"]
