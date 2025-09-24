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


class IsBusinessUser(BasePermission):
    """
    Allows access only to authenticated users who are 'business' type.
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
    Object-level permission: the requester must be the business user on the order.
    Also requires the requester to be a 'business' user.
    """
    message = "You are not allowed to update this order."

    def has_permission(self, request, view):
        # Auth + business check at request-level
        if not IsBusinessUser().has_permission(request, view):
            return False
        return True

    def has_object_permission(self, request, view, obj):
        # Only the business party attached to the order can mutate it
        return obj.business_user_id == request.user.id
