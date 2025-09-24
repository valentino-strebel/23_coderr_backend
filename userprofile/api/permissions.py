from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsProfileOwnerOrReadOnly(BasePermission):
    """
    - Any authenticated user can READ a profile (GET).
    - Only the owner of the profile can WRITE (PATCH/PUT/DELETE).
    """

    message = "You do not have permission to modify this profile."

    def has_permission(self, request, view):
        # Require authentication for both read and write (per spec)
        return bool(request.user and request.user.is_authenticated)

    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True
        # obj is a Profile instance
        return getattr(obj, "user_id", None) == getattr(request.user, "id", None)
