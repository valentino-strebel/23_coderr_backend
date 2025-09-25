"""
@file serializers.py
@description
    Provides serializers for Order creation, listing, and status updates.
"""

from django.db import transaction
from rest_framework import serializers

from orders.models import Order
from offers.models import OfferDetail


class OrderSerializer(serializers.ModelSerializer):
    """
    @serializer OrderSerializer
    @description
        Output serializer for listing orders, returning order creation results,
        and returning updated order results.
    @fields
        id {int} - Order ID
        customer_user {FK<User>} - Customer who placed the order
        business_user {FK<User>} - Business user receiving the order
        title {string} - Title snapshot from the offer detail
        revisions {int} - Revisions snapshot from the offer detail
        delivery_time_in_days {int} - Delivery time snapshot
        price {decimal} - Price snapshot
        features {list<string>} - Features snapshot
        offer_type {string} - Offer type snapshot
        status {string} - Current status of the order
        created_at {datetime} - When the order was created
        updated_at {datetime} - When the order was last updated
    """
    class Meta:
        model = Order
        fields = [
            "id",
            "customer_user",
            "business_user",
            "title",
            "revisions",
            "delivery_time_in_days",
            "price",
            "features",
            "offer_type",
            "status",
            "created_at",
            "updated_at",
        ]
        read_only_fields = fields


class OrderCreateSerializer(serializers.Serializer):
    """
    @serializer OrderCreateSerializer
    @description
        Input serializer for creating a new order from an OfferDetail.
        Validates that the offer exists and prevents users from ordering their own offers.
    @fields
        offer_detail_id {int} - Required, ID of the OfferDetail to order
    @errors
        - 400 if OfferDetail not found
        - 400 if customer tries to order their own offer
    """
    offer_detail_id = serializers.IntegerField(required=True, min_value=1)

    def validate_offer_detail_id(self, value):
        return value

    @transaction.atomic
    def create(self, validated_data):
        request = self.context.get("request")
        user = getattr(request, "user", None)
        offer_detail_id = validated_data["offer_detail_id"]

        try:
            od = OfferDetail.objects.select_related("offer__owner").get(pk=offer_detail_id)
        except OfferDetail.DoesNotExist:
            raise serializers.ValidationError(
                {"offer_detail_id": "OfferDetail not found."},
                code="not_found",
            )

        business_user = od.offer.owner

        if user.id == business_user.id:
            raise serializers.ValidationError(
                {"non_field_errors": "You cannot order your own offer."},
                code="permission_denied",
            )

        order = Order.objects.create(
            customer_user=user,
            business_user=business_user,
            offer_detail=od,
            title=od.title,
            revisions=od.revisions,
            delivery_time_in_days=od.delivery_time_in_days,
            price=od.price,
            features=od.features,
            offer_type=od.offer_type,
            status=Order.STATUS_IN_PROGRESS,
        )
        return order

    def to_representation(self, instance):
        return OrderSerializer(instance, context=self.context).data


class OrderStatusUpdateSerializer(serializers.ModelSerializer):
    """
    @serializer OrderStatusUpdateSerializer
    @description
        Input serializer for updating an order’s status via PATCH.
        Ensures only the `status` field is accepted.
        Returns the full order representation on success.
    @fields
        status {string} - New status value
    @errors
        - 400 if unexpected fields are provided
    """
    class Meta:
        model = Order
        fields = ["status"]

    def validate(self, attrs):
        extra_keys = set(self.initial_data.keys()) - {"status"}
        if extra_keys:
            raise serializers.ValidationError(
                {"non_field_errors": f"Only 'status' can be updated. Unexpected fields: {', '.join(sorted(extra_keys))}."}
            )
        return attrs

    def update(self, instance, validated_data):
        instance.status = validated_data["status"]
        instance.save(update_fields=["status", "updated_at"])
        return instance

    def to_representation(self, instance):
        return OrderSerializer(instance, context=self.context).data
