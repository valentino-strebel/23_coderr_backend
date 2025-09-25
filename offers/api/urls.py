"""
@file urls.py
@description
    Defines the URL routes for offer-related endpoints.

@routes
    GET  /api/offers/              - Public list of offers with filtering, search, ordering, pagination
    POST /api/offers/              - Create a new offer (business users only)
    GET  /api/offers/<id>/         - Retrieve an offer (authenticated users only)
    PATCH /api/offers/<id>/        - Update an offer (owner only)
    DELETE /api/offers/<id>/       - Delete an offer (owner only)
    GET  /api/offerdetails/<id>/   - Retrieve full offer detail (authenticated users only)

@imports
    OfferListCreateView
    OfferRetrieveUpdateDestroyView
    OfferDetailRetrieveView
"""

from django.urls import path
from .views import (
    OfferListCreateView,
    OfferRetrieveUpdateDestroyView,
    OfferDetailRetrieveView,
)

urlpatterns = [
    path("offers/", OfferListCreateView.as_view(), name="offer-list-create"),
    path("offers/<int:pk>/", OfferRetrieveUpdateDestroyView.as_view(), name="offer-detail"),
    path("offerdetails/<int:pk>/", OfferDetailRetrieveView.as_view(), name="offerdetail-detail"),
]
