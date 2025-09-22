from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsBusinessUser(BasePermission):
    """
    Allows access only to authenticated users who are 'business' type.
    Adjust the attribute checks to your actual User/Profile model.
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


class IsOfferOwner(BasePermission):
    """
    Only the owner of the Offer can modify or delete it.
    Authenticated users may read (GET).
    """
    message = "You do not have permission to modify this offer."

    def has_permission(self, request, view):
        # Must be authenticated for all actions on this view
        return bool(request.user and request.user.is_authenticated)

    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True
        return obj.owner_id == request.user.id
