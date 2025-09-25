from django.db.models import Min
from rest_framework import generics, filters, parsers, permissions
from rest_framework.pagination import PageNumberPagination

from offers.models import Offer, OfferDetail
from .serializers import (
    OfferSerializer,
    OfferListSerializer,
    OfferRetrieveSerializer,
    OfferDetailRetrieveSerializer,
    OfferUpdateSerializer,
)
from core.permissions import IsBusinessUser, IsOfferOwner


class OfferPagination(PageNumberPagination):
    """
    PageNumberPagination with ?page_size= support.
    """
    page_size = 10
    page_size_query_param = "page_size"
    max_page_size = 100


class OfferListCreateView(generics.ListCreateAPIView):
    """
    GET /api/offers/   -> public list with filtering/search/ordering/pagination
    POST /api/offers/  -> authenticated business users create an offer (exactly 3 details)
    """
    queryset = (
        Offer.objects.all()
        .select_related("owner")
        .prefetch_related("details")
    )
    parser_classes = [parsers.JSONParser, parsers.MultiPartParser, parsers.FormParser]
    pagination_class = OfferPagination

    # DRF search + ordering
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["title", "description"]
    ordering_fields = ["updated_at", "min_price"]
    ordering = ["-updated_at"]

    def get_permissions(self):
        if self.request.method.upper() == "POST":
            # Before: return [permissions.IsAuthenticated(), IsBusinessUser()]
            return [permissions.IsAuthenticated()]
        return [permissions.AllowAny()]

    #def get_permissions(self):
     #   if self.request.method.upper() == "POST":
      #      return [permissions.IsAuthenticated(), IsBusinessUser()]
       # return [permissions.AllowAny()]

    def get_serializer_class(self):
        if self.request.method.upper() == "POST":
            return OfferSerializer
        return OfferListSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        qp = self.request.query_params

        creator_id = qp.get("creator_id")
        min_price = qp.get("min_price")
        max_delivery_time = qp.get("max_delivery_time")

        if creator_id:
            qs = qs.filter(owner_id=creator_id)
        if min_price:
            qs = qs.filter(details__price__gte=min_price)
        if max_delivery_time:
            qs = qs.filter(details__delivery_time_in_days__lte=max_delivery_time)

        # Annotate for ordering by min_price
        qs = qs.annotate(min_price=Min("details__price"))
        return qs


class OfferRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    """
    GET /api/offers/<id>/     -> Auth required, returns detail links + min aggregates
    PATCH /api/offers/<id>/   -> Only owner may modify; partial update incl. details-by-offer_type
    DELETE /api/offers/<id>/  -> Only owner may delete; returns 204 No Content
    """
    queryset = (
        Offer.objects.all()
        .select_related("owner")
        .prefetch_related("details")
    )
    parser_classes = [parsers.JSONParser, parsers.MultiPartParser, parsers.FormParser]
    lookup_field = "pk"

    def get_permissions(self):
        if self.request.method.upper() in ("PATCH", "PUT", "DELETE"):
            return [IsOfferOwner()]
        # GET requires authentication
        return [permissions.IsAuthenticated()]

    def get_serializer_class(self):
        if self.request.method.upper() in ("PATCH", "PUT"):
            return OfferUpdateSerializer
        return OfferRetrieveSerializer


class OfferDetailRetrieveView(generics.RetrieveAPIView):
    """
    GET /api/offerdetails/<id>/
    Auth required. Returns full offer detail object.
    """
    queryset = OfferDetail.objects.all()
    serializer_class = OfferDetailRetrieveSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = "pk"
