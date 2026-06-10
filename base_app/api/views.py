# Third-party imports
from rest_framework.permissions import AllowAny
from django.db.models import Avg
from rest_framework import status
from rest_framework.filters import OrderingFilter
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

# Local imports
from auth_app.models import CustomUser
from base_app.models import Review
from marketplace_app.models import Offer
from marketplace_app.api.permissions import IsCustomerUser
from .permissions import IsReviewer
from .serializers import (
    BaseInfoSerializer,
    ReviewSerializer,
    ReviewUpdateSerializer
)


class ReviewListCreateView(ListCreateAPIView):
    """View for listing and creating reviews."""
    filter_backends = [OrderingFilter]
    ordering_fields = ['updated_at', 'rating']
    pagination_class = None

    def get_queryset(self):
        """Returns filtered queryset based on query parameters."""
        queryset = Review.objects.all()
        business_user_id = self.request.query_params.get('business_user_id')
        reviewer_id = self.request.query_params.get('reviewer_id')

        if business_user_id:
            queryset = queryset.filter(business_user_id=business_user_id)
        if reviewer_id:
            queryset = queryset.filter(reviewer_id=reviewer_id)

        return queryset

    def get_serializer_class(self):
        """Returns serializer based on request method."""
        return ReviewSerializer

    def get_permissions(self):
        """Returns permissions based on request method."""
        if self.request.method == 'POST':
            return [IsAuthenticated(), IsCustomerUser()]
        return [IsAuthenticated()]

    def create(self, request, *args, **kwargs):
        """Creates review and handles duplicate check."""
        serializer = ReviewSerializer(
            data=request.data,
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)

        already_exists = Review.objects.filter(
            business_user=serializer.validated_data['business_user'],
            reviewer=request.user
        ).exists()

        if already_exists:
            return Response(
                {"error": "You have already reviewed this business."},
                status=status.HTTP_400_BAD_REQUEST
            )

        review = serializer.save()
        return Response(
            ReviewSerializer(review, context={'request': request}).data,
            status=status.HTTP_201_CREATED
        )


class ReviewRetrieveUpdateDestroyView(RetrieveUpdateDestroyAPIView):
    """View for updating and deleting a specific review."""
    queryset = Review.objects.all()

    def get_serializer_class(self):
        """Returns serializer based on request method."""
        if self.request.method == 'PATCH':
            return ReviewUpdateSerializer
        return ReviewSerializer

    def get_permissions(self):
        """Returns permissions based on request method."""
        if self.request.method in ['PATCH', 'DELETE']:
            return [IsAuthenticated(), IsReviewer()]
        return [IsAuthenticated()]

    def get_object(self):
        """Returns review object and checks object permissions."""
        obj = super().get_object()
        self.check_object_permissions(self.request, obj)
        return obj

    def partial_update(self, request, *args, **kwargs):
        """Handles partial update of review."""
        kwargs['partial'] = True
        instance = self.get_object()
        serializer = ReviewUpdateSerializer(
            instance,
            data=request.data,
            partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(ReviewSerializer(instance).data)


class BaseInfoView(APIView):
    """View for retrieving platform statistics."""
    permission_classes = [AllowAny]

    def get(self, request):
        """Returns aggregated platform statistics."""
        review_count = Review.objects.count()

        avg = Review.objects.aggregate(Avg('rating'))['rating__avg']
        average_rating = round(avg, 1) if avg else 0.0

        business_profile_count = CustomUser.objects.filter(
            type='business'
        ).count()

        offer_count = Offer.objects.count()

        data = {
            'review_count': review_count,
            'average_rating': average_rating,
            'business_profile_count': business_profile_count,
            'offer_count': offer_count
        }

        serializer = BaseInfoSerializer(data)
        return Response(serializer.data)