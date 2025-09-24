from rest_framework.permissions import BasePermission


class IsCustomerUser(BasePermission):
    """
    Only authenticated users who are 'customer' type may create reviews.
    Adjust attribute names to your actual User/Profile model.
    """
    message = "Only authenticated users with a customer profile can perform this action."

    def has_permission(self, request, view):
        user = request.user
        if not user or not user.is_authenticated:
            return False

        # Option A: field on User
        if getattr(user, "user_type", None) == "customer":
            return True

        # Option B: field on related Profile
        profile = getattr(user, "profile", None)
        return getattr(profile, "type", None) == "customer"


class IsReviewOwner(BasePermission):
    """
    Only the creator (reviewer) of the review can modify it.
    """
    message = "You are not allowed to edit this review."

    def has_permission(self, request, view):
        # Must be authenticated to attempt the operation
        return bool(request.user and request.user.is_authenticated)

    def has_object_permission(self, request, view, obj):
        # Allow only the reviewer to modify
        return getattr(obj, "reviewer_id", None) == getattr(request.user, "id", None)
