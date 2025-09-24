from django.db import transaction
from rest_framework import serializers

from orders.models import Order
from offers.models import OfferDetail


class OrderSerializer(serializers.ModelSerializer):
    """
    Output serializer matching the success response spec.
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
        # Existence is checked in create() to return 404 semantics.
        return value

    @transaction.atomic
    def create(self, validated_data):
        request = self.context.get("request")
        user = getattr(request, "user", None)
        offer_detail_id = validated_data["offer_detail_id"]

        # 404 if offer detail is missing
        try:
            od = OfferDetail.objects.select_related("offer__owner").get(pk=offer_detail_id)
        except OfferDetail.DoesNotExist:
            raise serializers.ValidationError(
                {"offer_detail_id": "OfferDetail not found."},
                code="not_found",
            )

        business_user = od.offer.owner

        # 403: user cannot order own offer
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
        # Reuse the output serializer
        return OrderSerializer(instance, context=self.context).data
