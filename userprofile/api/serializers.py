"""
@file serializers.py
@description
    Serializers for profile retrieval, updates, and listing
    for business and customer user types.
"""

from django.contrib.auth import get_user_model
from rest_framework import serializers

from userprofile.models import Profile

User = get_user_model()


class ProfileSerializer(serializers.ModelSerializer):
    """
    @serializer ProfileSerializer
    @description
        Full profile serializer for retrieve and update operations.
        Ensures specified text fields are rendered as empty strings.
    @editable_fields
        first_name, last_name, email, file, location, tel, description, working_hours
    """
    user = serializers.PrimaryKeyRelatedField(read_only=True)
    username = serializers.CharField(source="user.username", read_only=True)
    email = serializers.EmailField(source="user.email", required=False, allow_blank=True)
    first_name = serializers.CharField(source="user.first_name", required=False, allow_blank=True)
    last_name = serializers.CharField(source="user.last_name", required=False, allow_blank=True)

    class Meta:
        model = Profile
        fields = [
            "user",
            "username",
            "first_name",
            "last_name",
            "file",
            "location",
            "tel",
            "description",
            "working_hours",
            "type",
            "email",
            "created_at",
        ]
        read_only_fields = ["user", "username", "type", "created_at"]

    # Normalize specific fields to empty strings per contract
    def to_representation(self, instance):
        data = super().to_representation(instance)
        for field in ["first_name", "last_name", "location", "tel", "description", "working_hours"]:
            if data.get(field) is None:
                data[field] = ""
        return data

    # Validate nested user updates (notably email)
    def validate(self, attrs):
        # Handle nested "user" dict from source="user.*"
        user_data = (attrs.get("user") or {}).copy()

        # Normalize incoming email (if provided) and validate uniqueness
        if "email" in user_data:
            raw_email = user_data.get("email")
            normalized = (raw_email or "").strip()

            if not normalized:
                # Treat empty/whitespace as "no change" unless you explicitly want to allow clearing.
                user_data.pop("email", None)
            else:
                qs = User.objects.filter(email__iexact=normalized)
                if self.instance:
                    qs = qs.exclude(pk=self.instance.user_id)
                if qs.exists():
                    # Keep error path under the nested structure
                    raise serializers.ValidationError({"user": {"email": "E-Mail wird bereits verwendet."}})
                user_data["email"] = normalized

        attrs["user"] = user_data
        return attrs

    def update(self, instance, validated_data):
        # Update nested User fields
        user_data = validated_data.pop("user", {})
        user = instance.user

        updated_user_fields = []
        for key in ["first_name", "last_name", "email"]:
            if key in user_data:
                setattr(user, key, user_data[key])
                updated_user_fields.append(key)
        if updated_user_fields:
            user.save(update_fields=updated_user_fields)

        # Update Profile fields
        for attr in ["file", "location", "tel", "description", "working_hours"]:
            if attr in validated_data:
                setattr(instance, attr, validated_data[attr])

        instance.save()
        return instance


class BusinessProfileListSerializer(serializers.ModelSerializer):
    """
    @serializer BusinessProfileListSerializer
    @description
        Serializer for listing all business profiles.
        Ensures specific text fields are returned as empty strings (not null).
    """
    user = serializers.PrimaryKeyRelatedField(read_only=True)
    username = serializers.CharField(source="user.username", read_only=True)
    first_name = serializers.CharField(source="user.first_name", read_only=True)
    last_name = serializers.CharField(source="user.last_name", read_only=True)

    class Meta:
        model = Profile
        fields = [
            "user",
            "username",
            "first_name",
            "last_name",
            "file",
            "location",
            "tel",
            "description",
            "working_hours",
            "type",
        ]
        read_only_fields = fields

    def to_representation(self, instance):
        data = super().to_representation(instance)
        for field in ["first_name", "last_name", "location", "tel", "description", "working_hours"]:
            if data.get(field) is None:
                data[field] = ""
        return data


class CustomerProfileListSerializer(serializers.ModelSerializer):
    """
    @serializer CustomerProfileListSerializer
    @description
        Serializer for listing all customer profiles.
        Adds `uploaded_at` mapped from `created_at`.
        Ensures specific text fields are returned as empty strings (not null).
    """
    user = serializers.PrimaryKeyRelatedField(read_only=True)
    username = serializers.CharField(source="user.username", read_only=True)
    first_name = serializers.CharField(source="user.first_name", read_only=True)
    last_name = serializers.CharField(source="user.last_name", read_only=True)
    uploaded_at = serializers.DateTimeField(source="created_at", read_only=True)

    class Meta:
        model = Profile
        fields = [
            "user",
            "username",
            "first_name",
            "last_name",
            "file",
            "location",
            "tel",
            "description",
            "working_hours",
            "type",
            "uploaded_at",
        ]
        read_only_fields = fields

    def to_representation(self, instance):
        data = super().to_representation(instance)
        for field in ["first_name", "last_name", "location", "tel", "description", "working_hours"]:
            if data.get(field) is None:
                data[field] = ""
        return data
