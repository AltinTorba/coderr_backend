# Third-party imports
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

# Local imports
from profiles_app.models import UserProfile
from .permissions import IsOwner
from .serializers import (
    BusinessProfileListSerializer,
    CustomerProfileListSerializer,
    UserProfileSerializer,
)


class ProfileView(APIView):
    """View to retrieve and update a user profile."""

    def get_permissions(self):
        """Set permissions based on request method."""
        if self.request.method == 'PATCH':
            permission_classes = [IsAuthenticated, IsOwner]
        else:
            permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]

    def _get_profile(self, pk):
        """Retrieve profile by user_id or return None."""
        try:
            return UserProfile.objects.get(user_id=pk)
        except UserProfile.DoesNotExist:
            return None

    def get(self, request, pk):
        """Get profile details for a specific user."""
        profile = self._get_profile(pk)
        if not profile:
            return Response(
                {"error": "Profile not found"},
                status=status.HTTP_404_NOT_FOUND
            )
        serializer = UserProfileSerializer(profile)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def patch(self, request, pk):
        """Update profile details for a specific user."""
        profile = self._get_profile(pk)
        if not profile:
            return Response(
                {"error": "Profile not found"},
                status=status.HTTP_404_NOT_FOUND
            )
        self.check_object_permissions(request, profile)
        serializer = UserProfileSerializer(profile, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class BusinessProfileListView(APIView):
    """View to list all business profiles."""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """Get list of all business profiles."""
        profiles = UserProfile.objects.filter(user__type='business')
        serializer = BusinessProfileListSerializer(profiles, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class CustomerProfileListView(APIView):
    """View to list all customer profiles."""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """Get list of all customer profiles."""
        profiles = UserProfile.objects.filter(user__type='customer')
        serializer = CustomerProfileListSerializer(profiles, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)