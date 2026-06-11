from rest_framework import permissions


class IsBusinessUser(permissions.BasePermission):
    """Permission to check if user is a business user."""

    def has_permission(self, request, view):
        """Check if the authenticated user has type 'business'."""
        return (
            request.user.is_authenticated
            and request.user.type == 'business'
        )


class IsCustomerUser(permissions.BasePermission):
    """Permission to check if user is a customer user."""

    def has_permission(self, request, view):
        """Check if the authenticated user has type 'customer'."""
        return (
            request.user.is_authenticated
            and request.user.type == 'customer'
        )


class IsOwner(permissions.BasePermission):
    """Permission to check if user is the owner of the object."""

    def has_object_permission(self, request, view, obj):
        """Check if the request user is the owner of the offer."""
        return obj.user == request.user


class IsBusinessOrderUser(permissions.BasePermission):
    """Permission to check if user is the business user of the order."""

    def has_object_permission(self, request, view, obj):
        """Check if the request user is the business user of the order."""
        return obj.business_user == request.user

