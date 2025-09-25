"""
@file urls.py
@description
    Defines the API routes for the base-info endpoint.

@routes
    GET /api/base-info/ - Public endpoint that returns statistics about reviews, ratings,
                          business profiles, and offers.

@imports
    BaseInfoView (from .views)

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
from django.urls import path
from .views import BaseInfoView

urlpatterns = [
    path("base-info/", BaseInfoView.as_view(), name="base-info"),
]
