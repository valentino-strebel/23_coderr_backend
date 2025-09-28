"""
@file views.py
@description
    Provides endpoints for creating, listing, retrieving, updating, and deleting offers.
    Includes filtering, search, ordering, and pagination.
"""

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
    OfferListQueryParamsSerializer,  # NEW: import the qp serializer
)
from core.permissions import IsBusinessUser, IsOfferOwner


class OfferPagination(PageNumberPagination):
    """
    @pagination OfferPagination
    @extends PageNumberPagination
    @description
        Paginator for offers with support for `?page_size` query parameter.
    @config
        page_size {int} = 10
        page_size_query_param = "page_size"
        max_page_size {int} = 100
    """
    page_size = 10
    page_size_query_param = "page_size"
    max_page_size = 100


class OfferListCreateView(generics.ListCreateAPIView):
    """
    @endpoint OfferListCreateView
    @route GET /api/offers/
    @route POST /api/offers/
    @auth
        GET  - Public
        POST - Authenticated business users only
    @description
        - GET: Returns a paginated list of offers with filtering, search, and ordering.
        - POST: Creates a new offer. Business users must provide exactly 3 details.

    @query_params
        creator_id {int} - Filter offers by creator ID
        min_price {decimal} - Filter offers with minimum price
        max_delivery_time {int} - Filter offers by maximum delivery time in days

    @filtering
        - Search fields: title, description
        - Ordering fields: updated_at, min_price
        - Default ordering: -updated_at
    """
    queryset = (
        Offer.objects.all()
        .select_related("owner")
        .prefetch_related("details")
    )
    parser_classes = [parsers.JSONParser, parsers.MultiPartParser, parsers.FormParser]
    pagination_class = OfferPagination
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["title", "description"]
    ordering_fields = ["updated_at", "min_price"]  # can order by annotated min_price
    ordering = ["-updated_at"]

    def get_permissions(self):
        if self.request.method.upper() == "POST":
            return [permissions.IsAuthenticated(), IsBusinessUser()]
        return [permissions.AllowAny()]

    def get_serializer_class(self):
        if self.request.method.upper() == "POST":
            return OfferSerializer
        return OfferListSerializer

    def get_queryset(self):
        base_qs = super().get_queryset()

        # Validate/coerce query params -> raises 400 on invalid instead of 500
        qp_serializer = OfferListQueryParamsSerializer(data=self.request.query_params)
        qp_serializer.is_valid(raise_exception=True)
        params = qp_serializer.validated_data

        qs = base_qs

        creator_id = params.get("creator_id")
        min_price = params.get("min_price")
        max_delivery_time = params.get("max_delivery_time")

        if creator_id is not None:
            qs = qs.filter(owner_id=creator_id)
        if min_price is not None:
            qs = qs.filter(details__price__gte=min_price)
        if max_delivery_time is not None:
            qs = qs.filter(details__delivery_time_in_days__lte=max_delivery_time)

        # Annotate aggregates used by serializers and ordering
        return qs.annotate(
            min_price=Min("details__price"),
            min_delivery_time=Min("details__delivery_time_in_days"),
        )


class OfferRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    """
    @endpoint OfferRetrieveUpdateDestroyView
    @route GET /api/offers/<id>/
    @route PATCH /api/offers/<id>/
    @route DELETE /api/offers/<id>/
    @auth
        GET    - Authenticated users
        PATCH  - Owner only
        DELETE - Owner only
    @description
        - GET: Returns offer details with related objects and aggregates.
        - PATCH: Allows owners to update offers, including details by offer_type.
        - DELETE: Allows owners to delete offers (returns 204 No Content).
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
        return [permissions.IsAuthenticated()]

    def get_serializer_class(self):
        if self.request.method.upper() in ("PATCH", "PUT"):
            return OfferUpdateSerializer
        return OfferRetrieveSerializer


class OfferDetailRetrieveView(generics.RetrieveAPIView):
    """
    @endpoint OfferDetailRetrieveView
    @route GET /api/offerdetails/<id>/
    @auth Authenticated users only
    @description
        Returns the full offer detail object.
    """
    queryset = OfferDetail.objects.all()
    serializer_class = OfferDetailRetrieveSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = "pk"
