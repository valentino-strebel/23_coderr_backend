"""
@file serializers.py
@description
    Serializers for profile retrieval, updates, and listing
    for business and customer user types.
"""

from rest_framework import serializers
from userprofile.models import Profile


class ProfileSerializer(serializers.ModelSerializer):
    """
    @serializer ProfileSerializer
    @description
        Full profile serializer for retrieve and update operations.
        Ensures nullable text fields are rendered as empty strings.
    @fields
        user {int} - User primary key (read-only)
        username {string} - Linked username (read-only)
        email {string} - Editable via PATCH
        first_name {string} - Editable via PATCH
        last_name {string} - Editable via PATCH
        file {file} - Optional profile file
        location {string}
        tel {string}
        description {string}
        working_hours {string}
        type {string} - Profile type (customer or business, read-only)
        created_at {datetime}
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

    def to_representation(self, instance):
        data = super().to_representation(instance)
        for field in ["first_name", "last_name", "location", "tel", "description", "working_hours"]:
            if data.get(field) is None:
                data[field] = ""
        return data

    def update(self, instance, validated_data):
        user_data = validated_data.pop("user", {})

        if "first_name" in user_data:
            instance.user.first_name = user_data["first_name"]
        if "last_name" in user_data:
            instance.user.last_name = user_data["last_name"]
        if "email" in user_data:
            instance.user.email = user_data["email"]
        instance.user.save()

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
    @fields
        user {int}
        username {string}
        first_name {string}
        last_name {string}
        file {file}
        location {string}
        tel {string}
        description {string}
        working_hours {string}
        type {string}
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
    @fields
        user {int}
        username {string}
        first_name {string}
        last_name {string}
        file {file}
        location {string}
        tel {string}
        description {string}
        working_hours {string}
        type {string}
        uploaded_at {datetime} - Alias for created_at
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
