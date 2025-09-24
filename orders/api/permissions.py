from rest_framework.permissions import BasePermission


class IsCustomerUser(BasePermission):
    """
    Allows access only to authenticated users who are 'customer' type.
    Adjust attribute names to match your User/Profile model.
    """
    message = "Authenticated user is not a 'customer' profile."

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
