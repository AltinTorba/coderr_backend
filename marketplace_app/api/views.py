# Third-party
from django.db.models import Min, Q
from rest_framework import status
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.generics import (
    ListCreateAPIView,
    RetrieveAPIView,
    RetrieveUpdateDestroyAPIView
)
from rest_framework.permissions import (
    IsAdminUser,
    IsAuthenticated,
    IsAuthenticatedOrReadOnly
)
from rest_framework.response import Response
from rest_framework.views import APIView

# Local
from auth_app.models import CustomUser
from marketplace_app.models import Offer, OfferDetail, Order
from .permissions import (
    IsBusinessOrderUser,
    IsBusinessUser,
    IsCustomerUser,
    IsOwner
)
from .serializers import (
    OfferDetailSerializer,
    OfferListSerializer,
    OfferRetrieveSerializer,
    OfferSerializer,
    OrderCreateSerializer,
    OrderSerializer,
    OrderStatusSerializer
)


class OfferListCreateView(ListCreateAPIView):
    """View for listing and creating offers."""
    filter_backends = [OrderingFilter, SearchFilter]
    search_fields = ['title', 'description']
    ordering_fields = ['updated_at', 'min_price']
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        """Returns annotated and filtered queryset."""
        queryset = Offer.objects.annotate(
            min_price=Min('details__price'),
            min_delivery_time=Min('details__delivery_time_in_days')
        ).select_related(
            'user'
        ).prefetch_related(
            'details'
        )

        creator_id = self.request.query_params.get('creator_id')
        min_price = self.request.query_params.get('min_price')
        max_delivery_time = self.request.query_params.get('max_delivery_time')

        if creator_id:
            queryset = queryset.filter(user=creator_id)
        if min_price:
            queryset = queryset.filter(min_price__gte=min_price)
        if max_delivery_time:
            queryset = queryset.filter(min_delivery_time__lte=max_delivery_time)

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


class OrderListCreateView(ListCreateAPIView):
    """View for listing and creating orders."""
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Returns orders for current user as customer or business."""
        user = self.request.user
        return Order.objects.filter(
            Q(customer_user=user) | Q(business_user=user)
        )

    def list(self, request, *args, **kwargs):
        """Returns list without pagination."""
        queryset = self.get_queryset()
        serializer = OrderSerializer(queryset, many=True)
        return Response(serializer.data)

    def get_serializer_class(self):
        """Returns serializer based on request method."""
        if self.request.method == 'POST':
            return OrderCreateSerializer
        return OrderSerializer

    def get_permissions(self):
        """Returns permissions based on request method."""
        if self.request.method == 'POST':
            return [IsAuthenticated(), IsCustomerUser()]
        return [IsAuthenticated()]

    def create(self, request, *args, **kwargs):
        """Creates order from offer detail."""
        serializer = OrderCreateSerializer(
            data=request.data,
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        order = serializer.save()
        return Response(
            OrderSerializer(order).data,
            status=status.HTTP_201_CREATED
        )


class OrderRetrieveUpdateDestroyView(RetrieveUpdateDestroyAPIView):
    """View for retrieving, updating and deleting a specific order."""
    queryset = Order.objects.all()
    serializer_class = OrderStatusSerializer

    def get_permissions(self):
        """Returns permissions based on request method."""
        if self.request.method == 'PATCH':
            return [IsAuthenticated(), IsBusinessOrderUser()]
        if self.request.method == 'DELETE':
            return [IsAuthenticated(), IsAdminUser()]
        return [IsAuthenticated()]

    def get_object(self):
        """Returns order object and checks permissions."""
        obj = super().get_object()
        self.check_object_permissions(self.request, obj)
        return obj

    def partial_update(self, request, *args, **kwargs):
        """Handles partial update of order status."""
        kwargs['partial'] = True
        instance = self.get_object()
        serializer = OrderStatusSerializer(
            instance,
            data=request.data,
            partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(OrderSerializer(instance).data)


class OrderCountView(APIView):
    """View for counting in_progress orders for a business user."""
    permission_classes = [IsAuthenticated]

    def get(self, request, business_user_id):
        """Returns count of in_progress orders."""
        if not CustomUser.objects.filter(id=business_user_id).exists():
            return Response(status=status.HTTP_404_NOT_FOUND)
        count = Order.objects.filter(
            business_user=business_user_id,
            status=Order.IN_PROGRESS
        ).count()
        return Response({'order_count': count})


class CompletedOrderCountView(APIView):
    """View for counting completed orders for a business user."""
    permission_classes = [IsAuthenticated]

    def get(self, request, business_user_id):
        """Returns count of completed orders."""
        if not CustomUser.objects.filter(id=business_user_id).exists():
            return Response(status=status.HTTP_404_NOT_FOUND)
        count = Order.objects.filter(
            business_user=business_user_id,
            status=Order.COMPLETED
        ).count()
        return Response({'completed_order_count': count})