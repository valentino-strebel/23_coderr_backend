"""
@file models.py
@description
    Defines the Order model, representing customer-to-business transactions
    with snapshotted offer details and workflow status.
"""

from django.conf import settings
from django.db import models


class Order(models.Model):
    """
    @model Order
    @description
        Represents an order placed by a customer for an offer detail from a business user.
        Includes snapshotted fields from the original OfferDetail to preserve history.

    @choices STATUS_CHOICES
        in_progress = "In Progress"
        completed   = "Completed"
        cancelled   = "Cancelled"

    @fields
        customer_user {FK<User>} - The customer who placed the order
        business_user {FK<User>} - The business receiving the order
        offer_detail {FK<OfferDetail>} - Optional reference to original offer detail (PROTECT)
        title {string} - Title snapshot from OfferDetail
        revisions {int} - Revisions snapshot from OfferDetail
        delivery_time_in_days {int} - Delivery time snapshot
        price {decimal} - Price snapshot from OfferDetail
        features {JSON} - Features snapshot from OfferDetail
        offer_type {string} - Offer type snapshot (basic, standard, premium)
        status {string} - Workflow status (in_progress, completed, cancelled)
        created_at {datetime} - Timestamp when the order was created
        updated_at {datetime} - Timestamp when the order was last updated
    """
    STATUS_IN_PROGRESS = "in_progress"
    STATUS_COMPLETED = "completed"
    STATUS_CANCELLED = "cancelled"

    STATUS_CHOICES = [
        (STATUS_IN_PROGRESS, "In Progress"),
        (STATUS_COMPLETED, "Completed"),
        (STATUS_CANCELLED, "Cancelled"),
    ]

    customer_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="orders_placed",
    )
    business_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="orders_received",
    )
    offer_detail = models.ForeignKey(
        "offers.OfferDetail",
        on_delete=models.PROTECT,
        related_name="orders",
        null=True,
        blank=True,
    )

    title = models.CharField(max_length=255)
    revisions = models.PositiveIntegerField()
    delivery_time_in_days = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    features = models.JSONField(default=list)
    offer_type = models.CharField(max_length=20)

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default=STATUS_IN_PROGRESS,
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return f"Order #{self.pk} — {self.title}"
