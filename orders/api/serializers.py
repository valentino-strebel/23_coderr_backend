from django.db import transaction
from rest_framework import serializers

from orders.models import Order
from offers.models import OfferDetail


class OrderSerializer(serializers.ModelSerializer):
    """
    Output serializer used for list, create result, and patch result.
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
    Input for POST /api/orders/
    """
    offer_detail_id = serializers.IntegerField(required=True, min_value=1)

    def validate_offer_detail_id(self, value):
        # Existence is checked in create() to keep a clean error message;
        # swap to view-level NotFound if you want strict 404 semantics.
        return value

    @transaction.atomic
    def create(self, validated_data):
        request = self.context.get("request")
        user = getattr(request, "user", None)
        offer_detail_id = validated_data["offer_detail_id"]

        # 404 if offer detail is missing (serializer ValidationError yields 400 by default;
        # if you want strict 404, move this to the view and raise NotFound)
        try:
            od = OfferDetail.objects.select_related("offer__owner").get(pk=offer_detail_id)
        except OfferDetail.DoesNotExist:
            raise serializers.ValidationError(
                {"offer_detail_id": "OfferDetail not found."},
                code="not_found",
            )

        business_user = od.offer.owner

        # 403-like: prevent ordering own offer
        if user.id == business_user.id:
            raise serializers.ValidationError(
                {"non_field_errors": "You cannot order your own offer."},
                code="permission_denied",
            )

        # Snapshot fields from OfferDetail
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
    For PATCH /api/orders/{id}/
    - Only 'status' is allowed in the payload.
    - Validates against model choices.
    - Returns FULL order payload after update.
    """
    class Meta:
        model = Order
        fields = ["status"]

    def validate(self, attrs):
        # Reject any unexpected fields (e.g., title, price, etc.)
        extra_keys = set(self.initial_data.keys()) - {"status"}
        if extra_keys:
            raise serializers.ValidationError(
                {"non_field_errors": f"Only 'status' can be updated. Unexpected fields: {', '.join(sorted(extra_keys))}."}
            )
        return attrs

    def update(self, instance, validated_data):
        # Only status is allowed here
        instance.status = validated_data["status"]
        instance.save(update_fields=["status", "updated_at"])
        return instance

    def to_representation(self, instance):
        # Return the full order object as per success response
        return OrderSerializer(instance, context=self.context).data
