from django.db import transaction
from django.db.models import Min
from rest_framework import serializers

from offers.models import Offer, OfferDetail


# ---------- Shared validators ----------
def _validate_features_list(value):
    if not isinstance(value, list):
        raise serializers.ValidationError("Features must be a list of strings.")
    if not all(isinstance(x, str) and x.strip() for x in value):
        raise serializers.ValidationError("Each feature must be a non-empty string.")
    return value


# ---------- Nested Detail (used for POST create) ----------
class OfferDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = OfferDetail
        fields = [
            "id",
            "title",
            "revisions",
            "delivery_time_in_days",
            "price",
            "features",
            "offer_type",
        ]
        read_only_fields = ["id"]

    def validate_features(self, value):
        return _validate_features_list(value)

    def validate(self, attrs):
        if attrs.get("revisions", 0) < 0:
            raise serializers.ValidationError({"revisions": "Must be zero or positive."})
        if attrs.get("delivery_time_in_days", 0) <= 0:
            raise serializers.ValidationError({"delivery_time_in_days": "Must be > 0."})
        if attrs.get("price") is not None and attrs["price"] < 0:
            raise serializers.ValidationError({"price": "Must be ≥ 0."})
        return attrs


# ---------- Offer create (POST /api/offers/) ----------
class OfferSerializer(serializers.ModelSerializer):
    details = OfferDetailSerializer(many=True)

    class Meta:
        model = Offer
        fields = ["id", "title", "image", "description", "details"]
        read_only_fields = ["id"]

    def validate_details(self, value):
        # Spec: exactly 3 details
        if not isinstance(value, list) or len(value) != 3:
            raise serializers.ValidationError("This offer must contain exactly 3 details.")
        allowed = {c[0] for c in OfferDetail.OFFER_TYPE_CHOICES}
        offer_types = []
        for d in value:
            t = d.get("offer_type")
            if t not in allowed:
                raise serializers.ValidationError(f"Invalid offer_type: {t}.")
            offer_types.append(t)
        if len(set(offer_types)) != len(offer_types):
            raise serializers.ValidationError("Each detail must have a unique offer_type.")
        return value

    @transaction.atomic
    def create(self, validated_data):
        details_data = validated_data.pop("details", [])
        request = self.context.get("request")
        owner = getattr(request, "user", None)

        offer = Offer.objects.create(owner=owner, **validated_data)
        OfferDetail.objects.bulk_create(
            [OfferDetail(offer=offer, **detail) for detail in details_data]
        )
        offer.refresh_from_db()
        return offer


# ---------- Lightweight link representation for details in list/retrieve ----------
class OfferDetailLinkSerializer(serializers.ModelSerializer):
    url = serializers.SerializerMethodField()

    class Meta:
        model = OfferDetail
        fields = ["id", "url"]

    def get_url(self, obj):
        request = self.context.get("request")
        path = f"/api/offerdetails/{obj.pk}/"
        return request.build_absolute_uri(path) if request else path


# ---------- Offer list (GET /api/offers/) ----------
class OfferListSerializer(serializers.ModelSerializer):
    details = OfferDetailLinkSerializer(many=True, read_only=True)
    min_price = serializers.SerializerMethodField()
    min_delivery_time = serializers.SerializerMethodField()
    user_details = serializers.SerializerMethodField()
    user = serializers.PrimaryKeyRelatedField(source="owner", read_only=True)

    class Meta:
        model = Offer
        fields = [
            "id",
            "user",
            "title",
            "image",
            "description",
            "created_at",
            "updated_at",
            "details",
            "min_price",
            "min_delivery_time",
            "user_details",
        ]

    def get_min_price(self, obj):
        return obj.details.aggregate(min_val=Min("price"))["min_val"]

    def get_min_delivery_time(self, obj):
        return obj.details.aggregate(min_val=Min("delivery_time_in_days"))["min_val"]

    def get_user_details(self, obj):
        u = obj.owner
        return {
            "first_name": u.first_name,
            "last_name": u.last_name,
            "username": u.username,
        }


# ---------- Offer retrieve (GET /api/offers/{id}/) ----------
class OfferRetrieveSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(source="owner", read_only=True)
    details = OfferDetailLinkSerializer(many=True, read_only=True)
    min_price = serializers.SerializerMethodField()
    min_delivery_time = serializers.SerializerMethodField()

    class Meta:
        model = Offer
        fields = [
            "id",
            "user",
            "title",
            "image",
            "description",
            "created_at",
            "updated_at",
            "details",
            "min_price",
            "min_delivery_time",
        ]

    def get_min_price(self, obj):
        return obj.details.aggregate(min_val=Min("price"))["min_val"]

    def get_min_delivery_time(self, obj):
        return obj.details.aggregate(min_val=Min("delivery_time_in_days"))["min_val"]


# ---------- Offer detail retrieve (GET /api/offerdetails/{id}/) ----------
class OfferDetailRetrieveSerializer(serializers.ModelSerializer):
    class Meta:
        model = OfferDetail
        fields = [
            "id",
            "title",
            "revisions",
            "delivery_time_in_days",
            "price",
            "features",
            "offer_type",
        ]


# ---------- PATCH support ----------
class OfferDetailPatchItemSerializer(serializers.Serializer):
    """
    One item inside the PATCH 'details' list.
    Identified by 'offer_type' (required). Other fields are optional.
    """
    offer_type = serializers.ChoiceField(choices=[c[0] for c in OfferDetail.OFFER_TYPE_CHOICES])
    title = serializers.CharField(required=False, allow_blank=False, max_length=255)
    revisions = serializers.IntegerField(required=False, min_value=0)
    delivery_time_in_days = serializers.IntegerField(required=False, min_value=1)
    price = serializers.DecimalField(required=False, max_digits=10, decimal_places=2, min_value=0)
    features = serializers.ListField(
        child=serializers.CharField(allow_blank=False),
        required=False
    )

    def validate_features(self, value):
        return _validate_features_list(value)


class OfferDetailFullSerializer(serializers.ModelSerializer):
    """Full detail representation for PATCH response."""
    class Meta:
        model = OfferDetail
        fields = [
            "id",
            "title",
            "revisions",
            "delivery_time_in_days",
            "price",
            "features",
            "offer_type",
        ]


class OfferUpdateSerializer(serializers.ModelSerializer):
    """
    For PATCH /api/offers/{id}/
    - Partially updates top-level fields (title, image, description).
    - Optionally updates any subset of details, matched by 'offer_type'.
    - Does not allow changing offer_type or detail IDs.
    """
    details = OfferDetailPatchItemSerializer(many=True, required=False)

    class Meta:
        model = Offer
        fields = ["id", "title", "image", "description", "details"]
        read_only_fields = ["id"]

    @transaction.atomic
    def update(self, instance, validated_data):
        # Update top-level fields if provided
        for field in ["title", "image", "description"]:
            if field in validated_data:
                setattr(instance, field, validated_data[field])
        instance.save()

        # Handle detail patches
        details_data = validated_data.get("details", None)
        if details_data is not None:
            # Map existing details by offer_type
            existing = {d.offer_type: d for d in instance.details.all()}

            for item in details_data:
                t = item.get("offer_type")
                if t not in existing:
                    raise serializers.ValidationError(
                        {"details": f"No existing detail with offer_type='{t}'."}
                    )
                detail = existing[t]
                # Update only provided fields (except offer_type/id)
                for field in ["title", "revisions", "delivery_time_in_days", "price", "features"]:
                    if field in item:
                        setattr(detail, field, item[field])
                detail.save(update_fields=[
                    f for f in ["title", "revisions", "delivery_time_in_days", "price", "features"]
                    if f in item
                ])

        # Return full offer representation with full details (per spec)
        return instance

    def to_representation(self, instance):
        # Build response: full offer with full details array
        data = {
            "id": instance.id,
            "title": instance.title,
            "image": instance.image.url if instance.image else None,
            "description": instance.description,
            "details": OfferDetailFullSerializer(instance.details.all(), many=True).data,
        }
        return data
