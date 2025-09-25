"""
@file serializers.py
@description
    Serializers for creating, listing, and updating reviews.
"""

from django.contrib.auth import get_user_model
from django.db import IntegrityError, transaction
from rest_framework import serializers

from reviews.models import Review


class ReviewSerializer(serializers.ModelSerializer):
    """
    @serializer ReviewSerializer
    @description
        Output serializer for reviews, used for list responses,
        create results, and patch results.
    @fields
        id {int}
        business_user {FK<User>}
        reviewer {FK<User>}
        rating {int} 1..5
        description {string}
        created_at {datetime}
        updated_at {datetime}
    """
    class Meta:
        model = Review
        fields = [
            "id",
            "business_user",
            "reviewer",
            "rating",
            "description",
            "created_at",
            "updated_at",
        ]
        read_only_fields = fields


class ReviewCreateSerializer(serializers.Serializer):
    """
    @serializer ReviewCreateSerializer
    @description
        Input serializer for POST /api/reviews/.
        Validates target business user, prevents self-reviews,
        and enforces a single review per (reviewer, business_user).
    @fields
        business_user {int} - ID of the business user being reviewed
        rating {int} - Required, 1..5
        description {string} - Optional
    @errors
        - 400 if target user not found or not a business
        - 400 if reviewer attempts to review themselves
        - 400 if a review already exists for this pair
    """
    business_user = serializers.IntegerField(required=True, min_value=1)
    rating = serializers.IntegerField(required=True, min_value=1, max_value=5)
    description = serializers.CharField(required=False, allow_blank=True)

    def validate_business_user(self, value: int):
        User = get_user_model()
        try:
            target = User.objects.get(pk=value)
        except User.DoesNotExist:
            raise serializers.ValidationError("Target business user not found.")

        is_business = False
        if getattr(target, "user_type", None) == "business":
            is_business = True
        else:
            profile = getattr(target, "profile", None)
            if getattr(profile, "type", None) == "business":
                is_business = True

        if not is_business:
            raise serializers.ValidationError("The specified user is not a business profile.")
        return value

    def validate(self, attrs):
        request = self.context.get("request")
        reviewer = getattr(request, "user", None)
        business_user_id = attrs.get("business_user")

        if reviewer and reviewer.id == business_user_id:
            raise serializers.ValidationError("You cannot review yourself.")

        if reviewer and business_user_id:
            exists = Review.objects.filter(
                reviewer_id=reviewer.id,
                business_user_id=business_user_id
            ).exists()
            if exists:
                raise serializers.ValidationError(
                    "You have already submitted a review for this business user."
                )
        return attrs

    @transaction.atomic
    def create(self, validated_data):
        request = self.context.get("request")
        reviewer = getattr(request, "user", None)

        try:
            review = Review.objects.create(
                business_user_id=validated_data["business_user"],
                reviewer_id=reviewer.id,
                rating=validated_data["rating"],
                description=validated_data.get("description", ""),
            )
        except IntegrityError:
            raise serializers.ValidationError(
                "You have already submitted a review for this business user."
            )
        return review

    def to_representation(self, instance):
        return ReviewSerializer(instance, context=self.context).data


class ReviewUpdateSerializer(serializers.ModelSerializer):
    """
    @serializer ReviewUpdateSerializer
    @description
        Input serializer for PATCH /api/reviews/{id}/.
        Only 'rating' and 'description' may be updated.
        Returns the full review representation on success.
    @fields
        rating {int} - Optional, 1..5
        description {string} - Optional
    """
    class Meta:
        model = Review
        fields = ["rating", "description"]
        extra_kwargs = {
            "rating": {"required": False, "min_value": 1, "max_value": 5},
            "description": {"required": False},
        }

    def validate(self, attrs):
        allowed = {"rating", "description"}
        extra = set(self.initial_data.keys()) - allowed
        if extra:
            raise serializers.ValidationError(
                {"non_field_errors": f"Only 'rating' and 'description' may be updated. Unexpected: {', '.join(sorted(extra))}."}
            )
        if not attrs:
            raise serializers.ValidationError("Provide at least one of: 'rating', 'description'.")
        return attrs

    def to_representation(self, instance):
        return ReviewSerializer(instance, context=self.context).data
