from django.contrib.auth import get_user_model, password_validation
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers

User = get_user_model()


class RegistrationSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=150)
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True, trim_whitespace=False)
    repeated_password = serializers.CharField(write_only=True, trim_whitespace=False)
    type = serializers.ChoiceField(choices=[("customer", "customer"), ("business", "business")])

    def validate_username(self, value):
        if User.objects.filter(username__iexact=value).exists():
            raise serializers.ValidationError(_("Username is already taken."))
        return value

    def validate_email(self, value):
        if User.objects.filter(email__iexact=value).exists():
            raise serializers.ValidationError(_("Email is already in use."))
        return value

    def validate(self, attrs):
        pw = attrs.get("password")
        rp = attrs.get("repeated_password")
        if pw != rp:
            raise serializers.ValidationError({"repeated_password": _("Passwords do not match.")})
        password_validation.validate_password(pw)
        return attrs

    def create(self, validated_data):
        validated_data.pop("repeated_password", None)
        user_type = validated_data.pop("type")
        user = User.objects.create_user(**validated_data, type=user_type)
        return user


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=150)
    password = serializers.CharField(write_only=True, trim_whitespace=False)

    # no create/update — this is only for validation in the view
