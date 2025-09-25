"""
@file urls.py
@description
    Defines authentication-related routes including registration and login.

@routes
    POST /api/auth/registration/ - Register a new user and return an auth token
    POST /api/auth/login/        - Authenticate an existing user and return an auth token

@imports
    RegistrationView (from .views)
    LoginView (from .views)

@example
    # Register a new user
    POST /api/auth/registration/
    {
        "username": "john_doe",
        "email": "john@example.com",
        "password": "securePass123",
        "type": "customer"
    }

    # Login with existing credentials
    POST /api/auth/login/
    {
        "username": "john_doe",
        "password": "securePass123"
    }
"""

from django.urls import path
from .views import RegistrationView, LoginView

urlpatterns = [
    path("registration/", RegistrationView.as_view(), name="registration"),
    path("login/", LoginView.as_view(), name="login"),
]
