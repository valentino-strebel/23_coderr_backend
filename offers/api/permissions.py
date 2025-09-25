"""
@file permissions.py
@description
    Custom DRF permission classes for business users and offer ownership.
"""

import logging
from rest_framework.permissions import BasePermission, SAFE_METHODS

logger = logging.getLogger(__name__)


class IsBusinessUser(BasePermission):
    """
    @permission IsBusinessUser
    @description
        Grants access only to authenticated users with role "business".
        Checks both `User.user_type` and `User.profile.type`.
        Accepts flexible representations (strings, numbers, enums).

    @config
        BUSINESS_ACCEPTED_STRINGS = {"business", "biz"}
        BUSINESS_ACCEPTED_NUMBERS = {2}
    """
    message = "Authenticated user is not a 'business' profile."
    BUSINESS_ACCEPTED_STRINGS = {"business", "biz"}
    BUSINESS_ACCEPTED_NUMBERS = {2}

    def _is_business(self, val):
        if val is None:
            return False

        if isinstance(val, str):
            return val.strip().lower() in self.BUSINESS_ACCEPTED_STRINGS

        if isinstance(val, int):
            return val in self.BUSINESS_ACCEPTED_NUMBERS

        for attr in ("name", "label", "value", "code", "slug", "key", "type"):
            if hasattr(val, attr):
                return self._is_business(getattr(val, attr))

        try:
            return str(val).strip().lower() in self.BUSINESS_ACCEPTED_STRINGS
        except Exception:
            return False

    def has_permission(self, request, view):
        user = request.user
        if not user or not user.is_authenticated:
            return False

        if self._is_business(getattr(user, "user_type", None)):
            return True

        profile = getattr(user, "profile", None)
        if self._is_business(getattr(profile, "type", None)):
            return True

        logger.info(
            "IsBusinessUser denied: user_id=%s user_type=%r profile_type=%r",
            getattr(user, "id", None),
            getattr(user, "user_type", None),
            getattr(profile, "type", None) if profile else None,
        )
        return False


class IsOfferOwner(BasePermission):
    """
    @permission IsOfferOwner
    @description
        Grants permission only to the owner of an Offer.
        - SAFE_METHODS (GET, HEAD, OPTIONS) allowed for any authenticated user.
        - Modification (PATCH, PUT, DELETE) requires ownership.
    """
    message = "You do not have permission to modify this offer."

    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated)

    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True
        return obj.owner_id == request.user.id
