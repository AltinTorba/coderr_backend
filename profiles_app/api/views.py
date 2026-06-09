# Third-party imports
from rest_framework.exceptions import NotFound
from rest_framework.generics import ListAPIView, RetrieveUpdateAPIView
from rest_framework.permissions import IsAuthenticated

# Local imports
from profiles_app.models import UserProfile
from .permissions import IsOwner
from .serializers import (
    BusinessProfileListSerializer,
    CustomerProfileListSerializer,
    UserProfileSerializer,
)


class ProfileView(RetrieveUpdateAPIView):
    """View to retrieve and update a user profile."""
    serializer_class = UserProfileSerializer
    http_method_names = ['get', 'patch']

    def get_permissions(self):
        """Returns permissions based on request method."""
        if self.request.method == 'PATCH':
            return [IsAuthenticated(), IsOwner()]
        return [IsAuthenticated()]

    def get_object(self):
        """Returns profile by user_id or raises 404."""
        try:
            obj = UserProfile.objects.get(user_id=self.kwargs['pk'])
        except UserProfile.DoesNotExist:
            raise NotFound("Profile not found.")
        self.check_object_permissions(self.request, obj)
        return obj


class BusinessProfileListView(ListAPIView):
    """View to list all business profiles."""
    serializer_class = BusinessProfileListSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = None
    queryset = UserProfile.objects.filter(user__type='business')


class CustomerProfileListView(ListAPIView):
    """View to list all customer profiles."""
    serializer_class = CustomerProfileListSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = None
    queryset = UserProfile.objects.filter(user__type='customer')