"""
@file urls.py
@description
    Defines the URL routes for order-related endpoints.

@routes
    GET  /api/orders/                         - List orders where the user is customer or business
    POST /api/orders/                         - Create a new order (customer users only)
    PATCH /api/orders/<id>/                   - Update order status (business party only)
    DELETE /api/orders/<id>/                  - Delete order (admin only)
    GET  /api/order-count/<business_user_id>/ - Count in-progress orders for a business user
    GET  /api/completed-order-count/<business_user_id>/ - Count completed orders for a business user

@imports
    OrderListCreateView
    OrderUpdateDestroyView
    OrderInProgressCountView
    OrderCompletedCountView
"""

from django.urls import path
from .views import (
    OrderListCreateView,
    OrderUpdateDestroyView,
    OrderInProgressCountView,
    OrderCompletedCountView,
)

urlpatterns = [
    path("orders/", OrderListCreateView.as_view(), name="order-list-create"),
    path("orders/<int:pk>/", OrderUpdateDestroyView.as_view(), name="order-update-destroy"),
    path("order-count/<int:business_user_id>/", OrderInProgressCountView.as_view(), name="order-in-progress-count"),
    path("completed-order-count/<int:business_user_id>/", OrderCompletedCountView.as_view(), name="order-completed-count"),
]
