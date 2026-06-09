# Third-party imports
from rest_framework import permissions


class IsReviewer(permissions.BasePermission):
    """Permission to check if user is the creator of the review."""

    def has_object_permission(self, request, view, obj):
        """Check if the request user is the reviewer."""
        return obj.reviewer == request.user