"""
@file permissions.py
@description
    Custom permission classes for reviews: restrict creation to customers
    and enforce object-level ownership for modifications.
"""

from rest_framework.permissions import BasePermission


class IsCustomerUser(BasePermission):
    """
    @permission IsCustomerUser
    @description
        Grants access only to authenticated users with type "customer".
        Checks both `User.user_type` and `User.profile.type`.
    @usage
        Used to restrict review creation (POST /api/reviews/).
    """
    message = "Only authenticated users with a customer profile can perform this action."

    def has_permission(self, request, view):
        user = request.user
        if not user or not user.is_authenticated:
            return False

        if getattr(user, "user_type", None) == "customer":
            return True

        profile = getattr(user, "profile", None)
        return getattr(profile, "type", None) == "customer"


class IsReviewOwner(BasePermission):
    """
    @permission IsReviewOwner
    @description
        Grants object-level access only to the reviewer who created the review.
        Used for update and delete operations.
    @usage
        Ensures only the original author can modify or delete their review.
    """
    message = "You are not allowed to edit this review."

    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated)

    def has_object_permission(self, request, view, obj):
        return getattr(obj, "reviewer_id", None) == getattr(request.user, "id", None)
