"""
@file urls.py
@description
    Defines URL routes for review-related endpoints.

@routes
    GET  /api/reviews/           - List reviews (auth required, with optional filters)
    POST /api/reviews/           - Create a new review (auth + customer required)
    PATCH /api/reviews/<id>/     - Update an existing review (auth + review owner required)
    DELETE /api/reviews/<id>/    - Delete an existing review (auth + review owner required)

@imports
    ReviewListCreateView
    ReviewUpdateDestroyView
"""

from django.urls import path
from .views import ReviewListCreateView, ReviewUpdateDestroyView

urlpatterns = [
    path("reviews/", ReviewListCreateView.as_view(), name="review-list-create"),
    path("reviews/<int:pk>/", ReviewUpdateDestroyView.as_view(), name="review-update-destroy"),
]
