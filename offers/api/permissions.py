from rest_framework.permissions import BasePermission, SAFE_METHODS
import logging

logger = logging.getLogger(__name__)


class IsBusinessUser(BasePermission):
    """
    Allows access only to authenticated users who are of 'business' type.
    Checks both User.user_type and User.profile.type.
    """

    message = "Authenticated user is not a 'business' profile."

    # Adjust these sets to match your actual model values
    BUSINESS_ACCEPTED_STRINGS = {"business", "biz"}
    BUSINESS_ACCEPTED_NUMBERS = {2}  # e.g., enum/int for "business"

    def _is_business(self, val):
        """Return True if the given value represents a 'business' user."""
        if val is None:
            return False

        # Strings
        if isinstance(val, str):
            return val.strip().lower() in self.BUSINESS_ACCEPTED_STRINGS

        # Numbers / enums stored as ints
        if isinstance(val, int):
            return val in self.BUSINESS_ACCEPTED_NUMBERS

        # Enum types or model instances: check common attributes
        for attr in ("name", "label", "value", "code", "slug", "key", "type"):
            if hasattr(val, attr):
                return self._is_business(getattr(val, attr))

        # Last resort: stringification
        try:
            return str(val).strip().lower() in self.BUSINESS_ACCEPTED_STRINGS
        except Exception:
            return False

    def has_permission(self, request, view):
        user = request.user
        if not user or not user.is_authenticated:
            return False

        # Direct field on user model
        if self._is_business(getattr(user, "user_type", None)):
            return True

        # Fallback: profile.type
        profile = getattr(user, "profile", None)
        if self._is_business(getattr(profile, "type", None)):
            return True

        # Log for debugging
        logger.info(
            "IsBusinessUser denied: user_id=%s user_type=%r profile_type=%r",
            getattr(user, "id", None),
            getattr(user, "user_type", None),
            getattr(profile, "type", None) if profile else None,
        )
        return False


class IsOfferOwner(BasePermission):
    """
    Only the owner of the Offer can modify or delete it.
    SAFE_METHODS (GET, HEAD, OPTIONS) are allowed for authenticated users.
    """

    message = "You do not have permission to modify this offer."

    def has_permission(self, request, view):
        # Must be authenticated for all actions on this view
        return bool(request.user and request.user.is_authenticated)

    def has_object_permission(self, request, view, obj):
        # Allow read-only methods for any authenticated user
        if request.method in SAFE_METHODS:
            return True
        # Write/delete requires ownership
        return obj.owner_id == request.user.id
