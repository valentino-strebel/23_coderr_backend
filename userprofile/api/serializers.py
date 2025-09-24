from rest_framework import serializers
from userprofile.models import Profile


class ProfileSerializer(serializers.ModelSerializer):
    # User-side fields
    user = serializers.PrimaryKeyRelatedField(read_only=True)
    username = serializers.CharField(source="user.username", read_only=True)
    email = serializers.EmailField(source="user.email", required=False)  # editable via PATCH
    first_name = serializers.CharField(
        source="user.first_name", required=False, allow_blank=True
    )
    last_name = serializers.CharField(
        source="user.last_name", required=False, allow_blank=True
    )

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
        """
        Ensure no null values for specific string fields — replace with ''.
        """
        data = super().to_representation(instance)
        for field in [
            "first_name",
            "last_name",
            "location",
            "tel",
            "description",
            "working_hours",
        ]:
            if data.get(field) is None:
                data[field] = ""
        return data

    def update(self, instance, validated_data):
        """
        Supports partial updates on:
        - User fields: first_name, last_name, email
        - Profile fields: file, location, tel, description, working_hours
        """
        user_data = validated_data.pop("user", {})

        # Update User fields if provided
        if "first_name" in user_data:
            instance.user.first_name = user_data["first_name"]
        if "last_name" in user_data:
            instance.user.last_name = user_data["last_name"]
        if "email" in user_data:
            instance.user.email = user_data["email"]
        instance.user.save()

        # Update Profile fields (partial)
        for attr in ["file", "location", "tel", "description", "working_hours"]:
            if attr in validated_data:
                setattr(instance, attr, validated_data[attr])

        instance.save()
        return instance


class BusinessProfileListSerializer(serializers.ModelSerializer):
    """
    List serializer for /api/profiles/business/
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
        for field in [
            "first_name",
            "last_name",
            "location",
            "tel",
            "description",
            "working_hours",
        ]:
            if data.get(field) is None:
                data[field] = ""
        return data


class CustomerProfileListSerializer(serializers.ModelSerializer):
    """
    List serializer for /api/profiles/customer/
    Includes 'uploaded_at' (mapped from created_at) to match example.
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
        for field in [
            "first_name",
            "last_name",
            "location",
            "tel",
            "description",
            "working_hours",
        ]:
            if data.get(field) is None:
                data[field] = ""
        return data
