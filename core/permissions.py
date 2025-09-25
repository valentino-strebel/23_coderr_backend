# permissions.py
from __future__ import annotations

import logging
from typing import Any, Iterable, Optional

from rest_framework.permissions import BasePermission, SAFE_METHODS

logger = logging.getLogger(__name__)


# -------------------------
# Helpers
# -------------------------

def _safe_get(obj: Any, attr: str, default: Any = None) -> Any:
    """Safely getattr with default."""
    try:
        return getattr(obj, attr, default)
    except Exception:  # pragma: no cover
        return default


def _normalize(val: Any) -> Optional[str]:
    """Stringify + normalize for loose equality."""
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
    Return True if 'candidate' represents any of the accepted roles.

    Handles:
    - raw strings: "business", "customer", etc.
    - ints/enums stored as ints
    - enum-like objects (checks common attributes)
    - last-resort stringification
    """
    if candidate is None:
        return False

    # Strings
    if isinstance(candidate, str):
        return _normalize(candidate) in {s.lower() for s in accepted_strings}

    # Ints / enum-as-int
    if isinstance(candidate, int):
        return candidate in set(accepted_numbers)

    # Enum-like / object w/ informative attrs
    for attr in probe_attrs:
        if hasattr(candidate, attr):
            if _is_any_role(getattr(candidate, attr), accepted_strings, accepted_numbers, probe_attrs):
                return True

    # Last resort: stringify
    n = _normalize(candidate)
    return n in {s.lower() for s in accepted_strings} if n is not None else False


def _user_is_authenticated(request) -> bool:
    user = getattr(request, "user", None)
    return bool(user and getattr(user, "is_authenticated", False))


def _user_matches_role(
    user: Any,
    role_strings: Iterable[str],
    role_numbers: Iterable[int] = (),
    user_role_attr: str = "type",          # <-- was "user_type"
    profile_attr: str = "profile",
    profile_role_attr: str = "type",
) -> bool:
    """
    Check role on user.<user_role_attr> first, then on user.<profile>.<profile_role_attr>.
    """
    # Direct field on user
    if _is_any_role(_safe_get(user, user_role_attr), role_strings, role_numbers):
        return True

    # Fallback: profile.<profile_role_attr>
    profile = _safe_get(user, profile_attr)
    return _is_any_role(_safe_get(profile, profile_role_attr), role_strings, role_numbers)


# -------------------------
# Role-based permissions
# -------------------------

class RolePermission(BasePermission):
    """
    Generic role gate. Subclass and set:
      ROLE_STRINGS = {"business"} (or {"customer"} ...)
      ROLE_NUMBERS = {2}            # optional
      message = "..."
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
    Allows access only to authenticated users who are 'business' type.
    Accepts flexible representations (strings, ints, enums).
    """
    message = "Authenticated user is not a 'business' profile."
    ROLE_STRINGS = {"business", "biz"}
    ROLE_NUMBERS = {2}  # adjust to your enum/int mapping as needed


class IsCustomerUser(RolePermission):
    """
    Allows access only to authenticated users who are 'customer' type.
    """
    message = "Authenticated user is not a 'customer' profile."
    ROLE_STRINGS = {"customer"}
    ROLE_NUMBERS = set()  # adjust if you also use ints for this role


# -------------------------
# Generic ownership permissions
# -------------------------

class IsAuthenticatedOnly(BasePermission):
    """Require an authenticated user for view access."""
    def has_permission(self, request, view):
        return _user_is_authenticated(request)


class IsOwner(BasePermission):
    """
    Generic object-level owner check. Configure via subclass OR set class attrs:

      OWNER_ID_FIELD = "owner_id"   # attribute on the object to compare
      USER_ID_FIELD  = "id"         # attribute on request.user to compare

    Example subclasses:
      - class IsOfferOwner(IsOwner): OWNER_ID_FIELD = "owner_id"
      - class IsReviewOwner(IsOwner): OWNER_ID_FIELD = "reviewer_id"
    """
    message = "You do not have permission to modify this resource."
    OWNER_ID_FIELD = "owner_id"
    USER_ID_FIELD = "id"

    def has_permission(self, request, view):
        # Typically require auth to even try object ops
        return _user_is_authenticated(request)

    def has_object_permission(self, request, view, obj):
        return _safe_get(obj, self.OWNER_ID_FIELD) == _safe_get(request.user, self.USER_ID_FIELD)


class IsOwnerOrReadOnly(IsOwner):
    """
    Read allowed (SAFE_METHODS) for authenticated users; write only if owner.
    """
    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True
        return super().has_object_permission(request, view, obj)


# -------------------------
# Concrete reuse of generics
# -------------------------

class IsOfferOwner(IsOwnerOrReadOnly):
    message = "You do not have permission to modify this offer."
    OWNER_ID_FIELD = "owner_id"


class IsReviewOwner(IsOwner):
    message = "You are not allowed to edit this review."
    OWNER_ID_FIELD = "reviewer_id"


class IsProfileOwnerOrReadOnly(IsOwnerOrReadOnly):
    message = "You do not have permission to modify this profile."
    OWNER_ID_FIELD = "user_id"


class IsOrderBusinessUser(BasePermission):
    """
    Request-level: must be a business user.
    Object-level: must be the business party attached to the order.
    """
    message = "You are not allowed to update this order."
    ORDER_BUSINESS_FIELD = "business_user_id"
    USER_ID_FIELD = "id"

    def has_permission(self, request, view):
        return IsBusinessUser().has_permission(request, view)

    def has_object_permission(self, request, view, obj):
        return _safe_get(obj, self.ORDER_BUSINESS_FIELD) == _safe_get(request.user, self.USER_ID_FIELD)
