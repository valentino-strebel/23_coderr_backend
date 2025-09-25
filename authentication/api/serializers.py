"""
@file serializers.py
@description
    Provides serializers for user registration and login.

@serializers
    RegistrationSerializer - Handles user creation with validation for unique username/email,
                             password confirmation, and password strength.
    LoginSerializer        - Validates login credentials for authentication.

@dependencies
    - django.contrib.auth.get_user_model
    - django.contrib.auth.password_validation
    - django.utils.translation
    - rest_framework.serializers
"""

from django.contrib.auth import get_user_model, password_validation
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers

User = get_user_model()


class RegistrationSerializer(serializers.Serializer):
    """
    @name RegistrationSerializer
    @description
        Validates and creates a new user with username, email, password confirmation,
        and user type. Ensures unique username/email and applies password validation rules.

    @fields
        username {string} - Required, max length 150
        email {string} - Required, unique, valid email format
        password {string} - Required, write-only, validated
        repeated_password {string} - Required, must match password
        type {string} - Required, must be one of User.USER_TYPE_CHOICES

    @validation
        - Username must be unique (case insensitive)
        - Email must be unique (case insensitive)
        - Passwords must match
        - Password must pass Django’s password validation rules

    @returns {User} A newly created user instance
    """
    username = serializers.CharField(max_length=150)
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True, trim_whitespace=False)
    repeated_password = serializers.CharField(write_only=True, trim_whitespace=False)
    type = serializers.ChoiceField(choices=User.USER_TYPE_CHOICES)

    def validate_username(self, value):
        if User.objects.filter(username__iexact=value).exists():
            raise serializers.ValidationError(_("Benutzername ist bereits vergeben."))
        return value

    def validate_email(self, value):
        if User.objects.filter(email__iexact=value).exists():
            raise serializers.ValidationError(_("E-Mail wird bereits verwendet."))
        return value

    def validate(self, attrs):
        pw = attrs.get("password")
        rp = attrs.get("repeated_password")
        if pw != rp:
            raise serializers.ValidationError({"repeated_password": _("Passwörter stimmen nicht überein.")})
        temp_user = User(
            username=attrs.get("username"),
            email=attrs.get("email"),
            type=attrs.get("type"),
        )
        password_validation.validate_password(pw, user=temp_user)
        return attrs

    def create(self, validated_data):
        validated_data.pop("repeated_password", None)
        user_type = validated_data.pop("type")
        user = User.objects.create_user(**validated_data, type=user_type)
        return user


class LoginSerializer(serializers.Serializer):
    """
    @name LoginSerializer
    @description
        Validates login credentials. Used in LoginView for authentication.

    @fields
        username {string} - Required, max length 150
        password {string} - Required, write-only
    """
    username = serializers.CharField(max_length=150)
    password = serializers.CharField(write_only=True, trim_whitespace=False)
