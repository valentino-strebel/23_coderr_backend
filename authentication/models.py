"""
@file models.py
@description
    Defines the custom User model extending Django's AbstractUser.
    Adds email uniqueness enforcement and a user type field.

@models
    User - Extends AbstractUser with email (unique) and type (customer/business).
"""

from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """
    @model User
    @extends AbstractUser
    @description
        Custom user model with enforced unique email and a user type field
        distinguishing between customers and businesses.

    @fields
        username {string} - Inherited from AbstractUser, required, unique
        email {string} - Unique email address
        type {string} - User type, either "customer" or "business"
        first_name {string} - Inherited from AbstractUser
        last_name {string} - Inherited from AbstractUser
        password {string} - Inherited from AbstractUser

    @choices
        CUSTOMER = "customer"
        BUSINESS = "business"

    @default
        type = CUSTOMER

    @example
        User.objects.create_user(
            username="jane_doe",
            email="jane@example.com",
            password="securePass123",
            type=User.BUSINESS
        )
    """
    CUSTOMER = "customer"
    BUSINESS = "business"
    USER_TYPE_CHOICES = [
        (CUSTOMER, "Customer"),
        (BUSINESS, "Business"),
    ]

    email = models.EmailField(unique=True)
    type = models.CharField(max_length=20, choices=USER_TYPE_CHOICES, default=CUSTOMER)

    def __str__(self):
        return f"{self.username} ({self.type})"
