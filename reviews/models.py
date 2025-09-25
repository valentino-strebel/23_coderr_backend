"""
@file models.py
@description
    Defines the Review model, representing customer feedback for business users.
"""

from django.conf import settings
from django.db import models


class Review(models.Model):
    """
    @model Review
    @description
        A review left by a customer for a business user.
        Each (reviewer, business_user) pair may only have one review.
    @fields
        business_user {FK<User>} - The business user being reviewed
        reviewer {FK<User>} - The customer writing the review
        rating {int} - Numeric rating (1–5)
        description {string} - Optional text feedback
        created_at {datetime} - Timestamp when the review was created
        updated_at {datetime} - Timestamp when the review was last updated
    @constraints
        unique_review_per_business_and_reviewer - Prevents duplicate reviews
    """
    business_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="business_reviews_received",
    )
    reviewer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="customer_reviews_written",
    )
    rating = models.PositiveSmallIntegerField()
    description = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["reviewer", "business_user"],
                name="unique_review_per_business_and_reviewer",
            )
        ]

    def __str__(self):
        return f"Review #{self.pk} — {self.reviewer_id} → {self.business_user_id} ({self.rating})"
