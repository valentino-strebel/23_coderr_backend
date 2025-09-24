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
