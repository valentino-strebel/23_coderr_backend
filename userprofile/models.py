"""
@file models.py
@description
    Defines the Profile model for extending user information with
    role-based types, contact details, and metadata.
"""

from django.conf import settings
from django.db import models


class Profile(models.Model):
    """
    @model Profile
    @description
        Extends the base User model with profile information.
        Supports both "customer" and "business" types.
    @choices USER_TYPE_CHOICES
        customer = "Customer"
        business = "Business"
    @fields
        user {OneToOne<User>} - Linked user (required, cascade on delete)
        file {ImageField} - Optional profile picture
        location {string} - User’s location
        tel {string} - Contact number
        description {string} - Profile description / bio
        working_hours {string} - Business working hours
        type {string} - Profile type (customer or business)
        created_at {datetime} - Timestamp when the profile was created
    """
    USER_TYPE_CHOICES = [
        ("customer", "Customer"),
        ("business", "Business"),
    ]

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="profile",
    )
    file = models.ImageField(upload_to="profile_pics/", blank=True, null=True)
    location = models.CharField(max_length=255, blank=True, default="")
    tel = models.CharField(max_length=50, blank=True, default="")
    description = models.TextField(blank=True, default="")
    working_hours = models.CharField(max_length=255, blank=True, default="")
    type = models.CharField(max_length=20, choices=USER_TYPE_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Profile of {self.user.username}"
