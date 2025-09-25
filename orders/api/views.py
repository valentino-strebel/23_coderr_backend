"""
@file views.py
@description
    Provides endpoints for creating, listing, updating, deleting, and counting orders.
"""

from django.contrib.auth import get_user_model
from rest_framework import generics, parsers, permissions, status
from rest_framework.response import Response
from rest_framework.exceptions import NotFound

from orders.models import Order
from .serializers import (
    OrderCreateSerializer,
    OrderSerializer,
    OrderStatusUpdateSerializer,
)
from core.permissions import IsCustomerUser, IsOrderBusinessUser


class OrderListCreateView(generics.ListCreateAPIView):
    """
    @endpoint OrderListCreateView
    @route GET /api/orders/
    @route POST /api/orders/
    @auth
        GET  - Authenticated users
        POST - Authenticated users of type 'customer'
    @description
        - GET: Returns only orders where the current user is either the customer or the business.
        - POST: Creates a new order from an offer_detail_id.
    """
    queryset = Order.objects.all()
    parser_classes = [parsers.JSONParser]

    def get_permissions(self):
        if self.request.method.upper() == "POST":
            return [permissions.IsAuthenticated(), IsCustomerUser()]
        return [permissions.IsAuthenticated()]

    def get_serializer_class(self):
        if self.request.method.upper() == "POST":
            return OrderCreateSerializer
        return OrderSerializer

    def get_queryset(self):
        user = self.request.user
        if not user or not user.is_authenticated:
            return Order.objects.none()
        return Order.objects.filter(customer_user=user) | Order.objects.filter(business_user=user)


class OrderUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    """
    @endpoint OrderUpdateDestroyView
    @route PATCH /api/orders/<id>/
    @route DELETE /api/orders/<id>/
    @auth
        PATCH  - Business party on the order
        DELETE - Admin users (is_staff)
    @description
        - PATCH: Allows the business party to update order status.
        - DELETE: Allows staff to delete an order (returns 204 No Content).
    """
    queryset = Order.objects.all()
    serializer_class = OrderStatusUpdateSerializer
    parser_classes = [parsers.JSONParser]
    lookup_field = "pk"
    http_method_names = ["patch", "delete"]

    def get_permissions(self):
        method = self.request.method.upper()
        if method == "PATCH":
            return [IsOrderBusinessUser()]
        if method == "DELETE":
            return [permissions.IsAdminUser()]
        return [permissions.IsAuthenticated()]


class _BusinessUserValidatorMixin:
    """
    @mixin _BusinessUserValidatorMixin
    @description
        Provides utility to validate that a given business_user_id corresponds to
        an existing user of type 'business'. Raises 404 otherwise.
    """
    def _get_and_validate_business_user(self, business_user_id: int):
        User = get_user_model()
        try:
            user = User.objects.get(pk=business_user_id)
        except User.DoesNotExist:
            raise NotFound("Business user not found.")

        is_business = False
        if getattr(user, "user_type", None) == "business":
            is_business = True
        else:
            profile = getattr(user, "profile", None)
            if getattr(profile, "type", None) == "business":
                is_business = True

        if not is_business:
            raise NotFound("Business user not found.")

        return user


class OrderInProgressCountView(_BusinessUserValidatorMixin, generics.GenericAPIView):
    """
    @endpoint OrderInProgressCountView
    @route GET /api/order-count/<business_user_id>/
    @auth Authenticated users
    @description
        Returns the count of in-progress orders for a given business user.
        Raises 404 if the user does not exist or is not a business.
    @response
        { "order_count": <int> }
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, business_user_id: int):
        self._get_and_validate_business_user(business_user_id)
        count = Order.objects.filter(
            business_user_id=business_user_id,
            status=Order.STATUS_IN_PROGRESS,
        ).count()
        return Response({"order_count": count}, status=status.HTTP_200_OK)


class OrderCompletedCountView(_BusinessUserValidatorMixin, generics.GenericAPIView):
    """
    @endpoint OrderCompletedCountView
    @route GET /api/completed-order-count/<business_user_id>/
    @auth Authenticated users
    @description
        Returns the count of completed orders for a given business user.
        Raises 404 if the user does not exist or is not a business.
    @response
        { "completed_order_count": <int> }
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, business_user_id: int):
        self._get_and_validate_business_user(business_user_id)
        count = Order.objects.filter(
            business_user_id=business_user_id,
            status=Order.STATUS_COMPLETED,
        ).count()
        return Response({"completed_order_count": count}, status=status.HTTP_200_OK)
