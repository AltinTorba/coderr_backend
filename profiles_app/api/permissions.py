# Third-party imports
from rest_framework import permissions


class IsOwner(permissions.BasePermission):
    """Permission to check if user is the owner of the profile."""

    def has_object_permission(self, request, view, obj):
        """Check if the request user is the owner of the profile."""
        return obj.user == request.user