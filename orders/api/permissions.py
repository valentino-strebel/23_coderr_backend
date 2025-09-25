"""
@file permissions.py
@description
    Custom DRF permission classes for customer and business user access control,
    as well as order-specific object-level checks.
"""

from rest_framework.permissions import BasePermission


class IsCustomerUser(BasePermission):
    """
    @permission IsCustomerUser
    @description
        Grants access only to authenticated users of type "customer".
        Checks both `User.user_type` and `User.profile.type`.
    """
    message = "Authenticated user is not a 'customer' profile."

    def has_permission(self, request, view):
        user = request.user
        if not user or not user.is_authenticated:
            return False

        if getattr(user, "user_type", None) == "customer":
            return True

        profile = getattr(user, "profile", None)
        return getattr(profile, "type", None) == "customer"


class IsBusinessUser(BasePermission):
    """
    @permission IsBusinessUser
    @description
        Grants access only to authenticated users of type "business".
        Checks both `User.user_type` and `User.profile.type`.
    """
    message = "Authenticated user is not a 'business' profile."

    def has_permission(self, request, view):
        user = request.user
        if not user or not user.is_authenticated:
            return False

        if getattr(user, "user_type", None) == "business":
            return True

        profile = getattr(user, "profile", None)
        return getattr(profile, "type", None) == "business"


class IsOrderBusinessUser(BasePermission):
    """
    @permission IsOrderBusinessUser
    @description
        Object-level permission ensuring that:
        - The requester is a business user, and
        - The requester is the business party attached to the order.
    """
    message = "You are not allowed to update this order."

    def has_permission(self, request, view):
        return IsBusinessUser().has_permission(request, view)

    def has_object_permission(self, request, view, obj):
        return obj.business_user_id == request.user.id
