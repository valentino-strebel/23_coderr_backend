"""
@file models.py
@description
    Defines the Offer and OfferDetail models for the offers app.
"""

from django.conf import settings
from django.db import models


class Offer(models.Model):
    """
    @model Offer
    @description
        Represents a top-level offer created by a business user.

    @fields
        owner {FK<User>} - The business user who owns this offer
        title {string} - Offer title, max length 255
        image {ImageField} - Optional image for the offer
        description {string} - Optional textual description
        created_at {datetime} - Timestamp when the offer was created
        updated_at {datetime} - Timestamp when the offer was last updated
    """
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="offers",
    )
    title = models.CharField(max_length=255)
    image = models.ImageField(upload_to="offers/", null=True, blank=True)
    description = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return self.title


class OfferDetail(models.Model):
    """
    @model OfferDetail
    @description
        Represents a specific tier/plan within an offer (e.g., basic, standard, premium).

    @fields
        offer {FK<Offer>} - The parent offer
        title {string} - Title of the offer detail
        revisions {int} - Number of revisions included (must be positive)
        delivery_time_in_days {int} - Delivery time in days (must be positive)
        price {decimal} - Price of the offer detail
        features {JSON} - List of feature strings
        offer_type {string} - Type of offer detail, one of "basic", "standard", "premium"

    @choices
        BASIC = "basic"
        STANDARD = "standard"
        PREMIUM = "premium"
    """
    BASIC = "basic"
    STANDARD = "standard"
    PREMIUM = "premium"
    OFFER_TYPE_CHOICES = [
        (BASIC, "Basic"),
        (STANDARD, "Standard"),
        (PREMIUM, "Premium"),
    ]

    offer = models.ForeignKey(
        Offer,
        on_delete=models.CASCADE,
        related_name="details",
    )
    title = models.CharField(max_length=255)
    revisions = models.PositiveIntegerField()
    delivery_time_in_days = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    features = models.JSONField(default=list)
    offer_type = models.CharField(max_length=20, choices=OFFER_TYPE_CHOICES)

    def __str__(self) -> str:
        return f"{self.offer.title} — {self.title}"
