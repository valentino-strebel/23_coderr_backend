"""
@file urls.py
@description
    Defines URL routes for user profile endpoints.

@routes
    GET  /api/profile/{id}/        - Retrieve a user profile (auth required)
    PATCH /api/profile/{id}/       - Update a profile (only owner allowed)
    GET  /api/profiles/business/   - List all business profiles (auth required)
    GET  /api/profiles/customer/   - List all customer profiles (auth required)

@imports
    ProfileRetrieveUpdateView
    BusinessProfileListView
    CustomerProfileListView
"""

from django.urls import path
from .views import (
    ProfileRetrieveUpdateView,
    BusinessProfileListView,
    CustomerProfileListView,
)

urlpatterns = [
    path("profile/<int:pk>/", ProfileRetrieveUpdateView.as_view(), name="profile-detail"),
    path("profiles/business/", BusinessProfileListView.as_view(), name="business-profiles"),
    path("profiles/customer/", CustomerProfileListView.as_view(), name="customer-profiles"),
]
