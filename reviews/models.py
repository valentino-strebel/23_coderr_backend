from django.conf import settings
from django.db import models


class Review(models.Model):
    """
    A review left by a customer for a business user.
    Enforces one review per (reviewer, business_user).
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
