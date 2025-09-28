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
        Ensures nullable text fields are rendered as empty strings.
    @editable_fields
        first_name, last_name, email, file, location, tel, description, working_hours
    """
    user = serializers.PrimaryKeyRelatedField(read_only=True)
    username = serializers.CharField(source="user.username", read_only=True)
    email = serializers.EmailField(source="user.email", required=False)
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

    # ✅ Return empty strings for specified fields per API contract
    def to_representation(self, instance):
        data = super().to_representation(instance)
        for field in ["first_name", "last_name", "location", "tel", "description", "working_hours"]:
            if data.get(field) is None:
                data[field] = ""
        return data

    # ✅ Prevent 500s on duplicate email by validating uniqueness on PATCH
    def validate(self, attrs):
        user_data = attrs.get("user", {})
        new_email = user_data.get("email")
        if new_email:
            qs = User.objects.filter(email__iexact=new_email)
            if self.instance:
                qs = qs.exclude(pk=self.instance.user_id)
            if qs.exists():
                raise serializers.ValidationError({"email": "E-Mail wird bereits verwendet."})
        return attrs

    def update(self, instance, validated_data):
        # Handle nested user fields from `source="user.*"`
        user_data = validated_data.pop("user", {})
        user = instance.user

        if "first_name" in user_data:
            user.first_name = user_data["first_name"]
        if "last_name" in user_data:
            user.last_name = user_data["last_name"]
        if "email" in user_data:
            user.email = user_data["email"]
        # Save user if anything changed
        if user_data:
            user.save(update_fields=[k for k in ["first_name", "last_name", "email"] if k in user_data])

        # Update profile fields
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
        Ensures nullable text fields are returned as empty strings.
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
        Adds `uploaded_at` mapped from `created_at` for clarity.
        Ensures nullable text fields are returned as empty strings.
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
