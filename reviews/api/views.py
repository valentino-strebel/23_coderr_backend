from rest_framework import generics, parsers, permissions, filters

from reviews.models import Review
from .serializers import ReviewCreateSerializer, ReviewSerializer, ReviewUpdateSerializer
from core.permissions import IsCustomerUser, IsReviewOwner


class ReviewListCreateView(generics.ListCreateAPIView):
    """
    GET /api/reviews/
      - Auth required
      - Optional filters:
          ?business_user_id=<int>
          ?reviewer_id=<int>
      - Ordering:
          ?ordering=updated_at | -updated_at | rating | -rating
      - Returns a (possibly paginated) list of reviews.

    POST /api/reviews/
      - Auth required AND requester must be a 'customer'
      - Body: { business_user, rating, description? }
      - Returns the created review (201)
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
    PATCH /api/reviews/<id>/
      - Auth required
      - Only the review author (reviewer) may update
      - Only 'rating' and 'description' are editable
      - Returns full review on success

    DELETE /api/reviews/<id>/
      - Auth required
      - Only the review author (reviewer) may delete
      - Returns 204 No Content on success
    """
    queryset = Review.objects.all()
    serializer_class = ReviewUpdateSerializer
    permission_classes = [permissions.IsAuthenticated, IsReviewOwner]
    parser_classes = [parsers.JSONParser]
    lookup_field = "pk"
    http_method_names = ["patch", "delete"]  # restrict to PATCH and DELETE
