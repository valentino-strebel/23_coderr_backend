from rest_framework import generics, parsers, permissions

from orders.models import Order
from .serializers import OrderCreateSerializer
from .permissions import IsCustomerUser


class OrderCreateView(generics.CreateAPIView):
    """
    POST /api/orders/
    Authenticated 'customer' users can create an order by providing offer_detail_id.
    Returns 201 with the created order.
    """
    queryset = Order.objects.all()
    serializer_class = OrderCreateSerializer
    permission_classes = [permissions.IsAuthenticated, IsCustomerUser]
    parser_classes = [parsers.JSONParser]
