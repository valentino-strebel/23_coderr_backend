"""
@file views.py
@description
    Provides authentication endpoints including user registration and login.
    Uses DRF's APIView and Token Authentication for stateless session handling.

@routes
    POST /api/auth/register/ - Register a new user and return an auth token
    POST /api/auth/login/    - Authenticate an existing user and return an auth token

@dependencies
    - django.contrib.auth.authenticate
    - django.db.transaction
    - rest_framework (APIView, Response, permissions, status, authtoken)
    - .serializers (RegistrationSerializer, LoginSerializer)
"""

from django.contrib.auth import authenticate
from django.db import IntegrityError, transaction

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework import status
from rest_framework.authtoken.models import Token

from .serializers import RegistrationSerializer, LoginSerializer


class RegistrationView(APIView):
    """
    @endpoint
    @name User Registration
    @route POST /api/auth/register/
    @auth Public (no authentication required)
    @description
        Registers a new user account. Creates the user in a transaction to ensure atomicity.
        On success, returns an authentication token and user details.

    @body {string} username - Desired username (must be unique)
    @body {string} email - Email address (must be unique)
    @body {string} password - Account password
    @body {string} type - User type (e.g., "business", "customer")

    @returns {Object} 201 - Created
    @returns {string} token - Authentication token
    @returns {string} username - Registered username
    @returns {string} email - Registered email
    @returns {number} user_id - Unique ID of the user
    @returns {string} type - User type

    @errors
        400 - Invalid data or username/email already exists
        500 - Internal server error

    @example
        # Request
        POST /api/auth/register/
        {
            "username": "john_doe",
            "email": "john@example.com",
            "password": "securePass123",
            "type": "customer"
        }

        # Response 201
        {
            "token": "abc123token",
            "username": "john_doe",
            "email": "john@example.com",
            "user_id": 42,
            "type": "customer"
        }
    """
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = RegistrationSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        try:
            with transaction.atomic():
                user = serializer.save()
        except IntegrityError:
            return Response(
                {"detail": "Benutzername oder E-Mail existiert bereits."},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception:
            return Response(
                {"detail": "Interner Serverfehler."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        token, _ = Token.objects.get_or_create(user=user)
        return Response(
            {
                "token": token.key,
                "username": user.username,
                "email": user.email,
                "user_id": user.pk,
                "type": user.type,
            },
            status=status.HTTP_201_CREATED
        )


class LoginView(APIView):
    """
    @endpoint
    @name User Login
    @route POST /api/auth/login/
    @auth Public (no authentication required)
    @description
        Authenticates an existing user with username and password.
        Returns an authentication token and user details on success.

    @body {string} username - Username of the account
    @body {string} password - Password of the account

    @returns {Object} 200 - Success
    @returns {string} token - Authentication token
    @returns {string} username - Authenticated username
    @returns {string} email - Authenticated email
    @returns {number} user_id - Unique ID of the user

    @errors
        400 - Invalid credentials or malformed data
        500 - Internal server error

    @example
        # Request
        POST /api/auth/login/
        {
            "username": "john_doe",
            "password": "securePass123"
        }

        # Response 200
        {
            "token": "abc123token",
            "username": "john_doe",
            "email": "john@example.com",
            "user_id": 42
        }
    """
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = LoginSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        username = serializer.validated_data["username"]
        password = serializer.validated_data["password"]

        try:
            user = authenticate(request=request, username=username, password=password)
        except Exception:
            return Response(
                {"detail": "Interner Serverfehler."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        if user is None:
            return Response(
                {"detail": "Ungültige Anmeldedaten."},
                status=status.HTTP_400_BAD_REQUEST
            )

        token, _ = Token.objects.get_or_create(user=user)
        data = {
            "token": token.key,
            "username": user.username,
            "email": user.email,
            "user_id": user.pk,
        }
        return Response(data, status=status.HTTP_200_OK)
