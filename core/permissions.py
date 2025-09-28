"""
@file permissions.py
@description
    Defines custom DRF permissions for role-based access control, ownership checks,
    and generic authentication requirements.

@permissions
    - RolePermission (base for role checks)
    - IsBusinessUser
    - IsCustomerUser
    - IsAuthenticatedOnly
    - IsOwner
    - IsOwnerOrReadOnly
    - IsOfferOwner
    - IsReviewOwner
    - IsProfileOwnerOrReadOnly
    - IsOrderBusinessUser

@helpers
    - _safe_get: Safe getattr with default
    - _normalize: Stringify + normalize values
    - _is_any_role: Flexible role matcher
    - _user_is_authenticated: Check user authentication
    - _user_matches_role: Match user against role definitions
"""

from __future__ import annotations

import logging
from typing import Any, Iterable, Optional

from rest_framework.permissions import BasePermission, SAFE_METHODS

logger = logging.getLogger(__name__)


def _safe_get(obj: Any, attr: str, default: Any = None) -> Any:
    """
    @helper _safe_get
    @description
        Safely retrieve an attribute from an object with a fallback default.
    """
    try:
        return getattr(obj, attr, default)
    except Exception:  # pragma: no cover
        return default


def _normalize(val: Any) -> Optional[str]:
    """
    @helper _normalize
    @description
        Stringify and normalize a value for loose equality checks.
    """
    if val is None:
        return None
    try:
        return str(val).strip().lower()
    except Exception:
        return None


def _is_any_role(
    candidate: Any,
    accepted_strings: Iterable[str],
    accepted_numbers: Iterable[int] = (),
    probe_attrs: Iterable[str] = ("name", "label", "value", "code", "slug", "key", "type"),
) -> bool:
    """
    @helper _is_any_role
    @description
        Determine if a candidate represents any of the accepted roles.

    @handles
        - Raw strings ("business", "customer")
        - Ints/enums stored as ints
        - Enum-like objects with common attributes
        - Fallback to stringification
    """
    if candidate is None:
        return False

    if isinstance(candidate, str):
        return _normalize(candidate) in {s.lower() for s in accepted_strings}

    if isinstance(candidate, int):
        return candidate in set(accepted_numbers)

    for attr in probe_attrs:
        if hasattr(candidate, attr):
            if _is_any_role(getattr(candidate, attr), accepted_strings, accepted_numbers, probe_attrs):
                return True

    n = _normalize(candidate)
    return n in {s.lower() for s in accepted_strings} if n is not None else False


def _user_is_authenticated(request) -> bool:
    """
    @helper _user_is_authenticated
    @description
        Check if the request has an authenticated user.
    """
    user = getattr(request, "user", None)
    return bool(user and getattr(user, "is_authenticated", False))


def _user_matches_role(
    user: Any,
    role_strings: Iterable[str],
    role_numbers: Iterable[int] = (),
    user_role_attr: str = "type",
    profile_attr: str = "profile",
    profile_role_attr: str = "type",
) -> bool:
    """
    @helper _user_matches_role
    @description
        Check a user's role, first directly on the user object,
        then on an associated profile object.
    """
    if _is_any_role(_safe_get(user, user_role_attr), role_strings, role_numbers):
        return True

    profile = _safe_get(user, profile_attr)
    return _is_any_role(_safe_get(profile, profile_role_attr), role_strings, role_numbers)


class RolePermission(BasePermission):
    """
    @permission RolePermission
    @description
        Base permission class for role-based checks.
        Subclass and define ROLE_STRINGS and optionally ROLE_NUMBERS.
    """
    ROLE_STRINGS: Iterable[str] = ()
    ROLE_NUMBERS: Iterable[int] = ()
    message = "You are not allowed to perform this action."

    def has_permission(self, request, view):
        if not _user_is_authenticated(request):
            return False
        user = request.user
        allowed = _user_matches_role(user, self.ROLE_STRINGS, self.ROLE_NUMBERS)
        if not allowed:
            logger.info(
                "%s denied: user_id=%s user_type=%r profile_type=%r",
                self.__class__.__name__,
                getattr(user, "id", None),
                getattr(user, "user_type", None),
                getattr(getattr(user, "profile", None), "type", None),
            )
        return allowed


class IsBusinessUser(RolePermission):
    """
    @permission IsBusinessUser
    @description
        Allows access only to authenticated users with type "business".
        Supports flexible role representations (strings, ints, enums).
    """
    message = "Authenticated user is not a 'business' profile."
    ROLE_STRINGS = {"business", "biz"}
    ROLE_NUMBERS = {2}


class IsCustomerUser(RolePermission):
    """
    @permission IsCustomerUser
    @description
        Allows access only to authenticated users with type "customer".
    """
    message = "Authenticated user is not a 'customer' profile."
    ROLE_STRINGS = {"customer"}
    ROLE_NUMBERS = set()


class IsAuthenticatedOnly(BasePermission):
    """
    @permission IsAuthenticatedOnly
    @description
        Requires that the request is made by an authenticated user.
    """
    def has_permission(self, request, view):
        return _user_is_authenticated(request)


class IsOwner(BasePermission):
    """
    @permission IsOwner
    @description
        Grants permission only if the requesting user is the owner of the object.

    @config
        OWNER_ID_FIELD = "owner_id"
        USER_ID_FIELD  = "id"
    """
    message = "You do not have permission to modify this resource."
    OWNER_ID_FIELD = "owner_id"
    USER_ID_FIELD = "id"

    def has_permission(self, request, view):
        return _user_is_authenticated(request)

    def has_object_permission(self, request, view, obj):
        return _safe_get(obj, self.OWNER_ID_FIELD) == _safe_get(request.user, self.USER_ID_FIELD)


class IsOwnerOrReadOnly(IsOwner):
    """
    @permission IsOwnerOrReadOnly
    @description
        Allows read access to authenticated users,
        but write access only if the user is the object owner.
    """
    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True
        return super().has_object_permission(request, view, obj)


class IsOfferOwner(IsOwnerOrReadOnly):
    """
    @permission IsOfferOwner
    @description
        Grants write permissions only to the owner of an offer.
    """
    message = "You do not have permission to modify this offer."
    OWNER_ID_FIELD = "owner_id"


class IsReviewOwner(IsOwner):
    """
    @permission IsReviewOwner
    @description
        Grants permission only to the owner of a review.
    """
    message = "You are not allowed to edit this review."
    OWNER_ID_FIELD = "reviewer_id"


class IsProfileOwnerOrReadOnly(IsOwnerOrReadOnly):
    """
    @permission IsProfileOwnerOrReadOnly
    @description
        Request-level: user must be authenticated (inherited).
        Object-level:
            - SAFE_METHODS (GET/HEAD/OPTIONS): allowed to authenticated users.
            - Write methods (PATCH/PUT/DELETE): only allowed when request.user.id == obj.user_id.
    """
    message = "You do not have permission to modify this profile."
    OWNER_ID_FIELD = "user_id"



class IsOrderBusinessUser(BasePermission):
    """
    @permission IsOrderBusinessUser
    @description
        Request-level: user must be a business.
        Object-level: user must be the business party attached to the order.
    """
    message = "You are not allowed to update this order."
    ORDER_BUSINESS_FIELD = "business_user_id"
    USER_ID_FIELD = "id"

    def has_permission(self, request, view):
        return IsBusinessUser().has_permission(request, view)

    def has_object_permission(self, request, view, obj):
        return _safe_get(obj, self.ORDER_BUSINESS_FIELD) == _safe_get(request.user, self.USER_ID_FIELD)
