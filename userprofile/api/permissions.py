"""
@file permissions.py
@description
    Custom permission class for profile access control.
"""

from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsProfileOwnerOrReadOnly(BasePermission):
    """
    @permission IsProfileOwnerOrReadOnly
    @description
        - Allows any authenticated user to read (GET) profiles.
        - Only the profile owner may modify (PATCH, PUT, DELETE).
    @message
        "You do not have permission to modify this profile."
    @usage
        Applied to profile retrieve/update views to enforce ownership rules.
    """
    message = "You do not have permission to modify this profile."

    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated)

    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True
        return getattr(obj, "user_id", None) == getattr(request.user, "id", None)
