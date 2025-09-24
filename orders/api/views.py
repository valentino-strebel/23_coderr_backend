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
from .permissions import IsCustomerUser, IsOrderBusinessUser


class OrderListCreateView(generics.ListCreateAPIView):
    """
    GET /api/orders/
      - Auth required
      - Returns ONLY orders where the current user is either the customer or the business

    POST /api/orders/
      - Auth required AND user must be of type 'customer'
      - Creates a new order from an offer_detail_id (see OrderCreateSerializer)
    """
    queryset = Order.objects.all()
    parser_classes = [parsers.JSONParser]

    def get_permissions(self):
        # POST requires customer users; GET just requires authentication
        if self.request.method.upper() == "POST":
            return [permissions.IsAuthenticated(), IsCustomerUser()]
        return [permissions.IsAuthenticated()]

    def get_serializer_class(self):
        if self.request.method.upper() == "POST":
            return OrderCreateSerializer
        return OrderSerializer

    def get_queryset(self):
        """
        Limit results to orders where the user is involved:
          - as customer_user OR
          - as business_user
        """
        user = self.request.user
        if not user or not user.is_authenticated:
            return Order.objects.none()
        return Order.objects.filter(customer_user=user) | Order.objects.filter(business_user=user)


class OrderUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    """
    PATCH /api/orders/<id>/
      -> Only the business party on the order may update the status
    DELETE /api/orders/<id>/
      -> Only staff (is_staff) may delete; returns 204 No Content
    """
    queryset = Order.objects.all()
    serializer_class = OrderStatusUpdateSerializer
    parser_classes = [parsers.JSONParser]
    lookup_field = "pk"
    http_method_names = ["patch", "delete"]  # restrict to PATCH and DELETE

    def get_permissions(self):
        method = self.request.method.upper()
        if method == "PATCH":
            # Business user on this order can update status
            return [IsOrderBusinessUser()]
        if method == "DELETE":
            # Staff-only delete
            return [permissions.IsAdminUser()]
        return [permissions.IsAuthenticated()]


class _BusinessUserValidatorMixin:
    """
    Mixin to validate that a given business_user_id exists and is a 'business' user.
    """

    def _get_and_validate_business_user(self, business_user_id: int):
        User = get_user_model()
        try:
            user = User.objects.get(pk=business_user_id)
        except User.DoesNotExist:
            raise NotFound("Business user not found.")

        # Verify this is a business user (adjust attribute names to your model)
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
    GET /api/order-count/<business_user_id>/
    - Auth required
    - Returns {'order_count': <int>} for orders with status='in_progress'
    - 404 if the user does not exist OR is not a 'business' user
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
    GET /api/completed-order-count/<business_user_id>/
    - Auth required
    - Returns {'completed_order_count': <int>} for orders with status='completed'
    - 404 if the user does not exist OR is not a 'business' user
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, business_user_id: int):
        self._get_and_validate_business_user(business_user_id)
        count = Order.objects.filter(
            business_user_id=business_user_id,
            status=Order.STATUS_COMPLETED,
        ).count()
        return Response({"completed_order_count": count}, status=status.HTTP_200_OK)
