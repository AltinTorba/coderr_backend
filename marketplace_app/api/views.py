# Third-party
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.generics import (
    ListCreateAPIView,
    RetrieveAPIView,
    RetrieveUpdateDestroyAPIView
)
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly

# Local
from marketplace_app.models import Offer, OfferDetail
from .permissions import IsBusinessUser, IsOwner
from .serializers import (
    OfferDetailSerializer,
    OfferListSerializer,
    OfferRetrieveSerializer,
    OfferSerializer
)


class OfferListCreateView(ListCreateAPIView):
    """View for listing and creating offers."""
    filter_backends = [OrderingFilter, SearchFilter]
    search_fields = ['title', 'description']
    ordering_fields = ['updated_at']
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        """Returns filtered queryset based on query parameters."""
        queryset = Offer.objects.all()
        creator_id = self.request.query_params.get('creator_id')
        if creator_id:
            queryset = queryset.filter(user=creator_id)
        return queryset

    def get_serializer_class(self):
        """Returns serializer based on request method."""
        if self.request.method == 'POST':
            return OfferSerializer
        return OfferListSerializer

    def get_permissions(self):
        """Returns permissions based on request method."""
        if self.request.method == 'POST':
            return [IsAuthenticated(), IsBusinessUser()]
        return super().get_permissions()

    def perform_create(self, serializer):
        """Saves offer with authenticated user as owner."""
        serializer.save(user=self.request.user)


class OfferRetrieveUpdateDestroyView(RetrieveUpdateDestroyAPIView):
    """View for retrieving, updating and deleting a specific offer."""
    queryset = Offer.objects.all()
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        """Returns serializer based on request method."""
        if self.request.method == 'GET':
            return OfferRetrieveSerializer
        return OfferSerializer

    def get_permissions(self):
        """Returns permissions based on request method."""
        if self.request.method in ['PATCH', 'DELETE']:
            return [IsAuthenticated(), IsOwner()]
        return [IsAuthenticated()]

    def get_object(self):
        """Returns offer object and checks permissions."""
        obj = super().get_object()
        self.check_object_permissions(self.request, obj)
        return obj
    
    def partial_update(self, request, *args, **kwargs):
        """Handles partial update of offer and its details."""
        kwargs['partial'] = True
        return self.update(request, *args, **kwargs)


class OfferDetailRetrieveView(RetrieveAPIView):
    """View for retrieving a specific offer detail."""
    queryset = OfferDetail.objects.all()
    serializer_class = OfferDetailSerializer
    permission_classes = [IsAuthenticated]