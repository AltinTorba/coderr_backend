# Third-party imports
from django.db.models import Min
from rest_framework import serializers

# Local imports
from marketplace_app.models import Offer, OfferDetail


class OfferDetailSerializer(serializers.ModelSerializer):
    """Serializer for full offer detail (create, read)."""

    class Meta:
        model = OfferDetail
        fields = [
            'id',
            'title',
            'revisions',
            'delivery_time_in_days',
            'price',
            'features',
            'offer_type'
        ]


class OfferDetailUpdateSerializer(serializers.ModelSerializer):
    """Serializer for partial update of offer detail."""
    offer_type = serializers.CharField()

    class Meta:
        model = OfferDetail
        fields = [
            'title',
            'revisions',
            'delivery_time_in_days',
            'price',
            'features',
            'offer_type'
        ]
        extra_kwargs = {
            'title': {'required': False},
            'revisions': {'required': False},
            'delivery_time_in_days': {'required': False},
            'price': {'required': False},
            'features': {'required': False},
        }


class OfferDetailUrlSerializer(serializers.ModelSerializer):
    """Serializer for offer detail with id and url only."""
    url = serializers.SerializerMethodField()

    def get_url(self, obj):
        """Returns the absolute URL for the offer detail."""
        request = self.context.get('request')
        if request:
            return request.build_absolute_uri(
                f'/api/offerdetails/{obj.id}/'
            )
        return f'/api/offerdetails/{obj.id}/'

    class Meta:
        model = OfferDetail
        fields = ['id', 'url']


class OfferMinValuesMixin:
    """Mixin that provides min_price and min_delivery_time methods."""

    def get_min_price(self, obj):
        """Returns the minimum price from offer details."""
        return obj.details.aggregate(Min('price'))['price__min']

    def get_min_delivery_time(self, obj):
        """Returns the minimum delivery time from offer details."""
        return obj.details.aggregate(
            Min('delivery_time_in_days')
        )['delivery_time_in_days__min']


class OfferSerializer(serializers.ModelSerializer):
    """Serializer for creating and updating offers with nested details."""
    details = OfferDetailSerializer(many=True)

    class Meta:
        model = Offer
        fields = [
            'id',
            'user',
            'title',
            'image',
            'description',
            'created_at',
            'updated_at',
            'details'
        ]
        read_only_fields = ['user', 'created_at', 'updated_at']

    def get_fields(self):
        """Returns fields based on request method."""
        fields = super().get_fields()
        request = self.context.get('request')
        if request and request.method == 'PATCH':
            fields['details'] = OfferDetailUpdateSerializer(
                many=True,
                required=False
            )
        return fields

    def validate_details(self, value):
        """Validates that exactly 3 details are provided for POST."""
        request = self.context.get('request')
        if request and request.method == 'POST':
            if len(value) != 3:
                raise serializers.ValidationError(
                    "An offer must contain exactly 3 details."
                )
        return value

    def create(self, validated_data):
        """Creates an offer with its nested details."""
        details_data = validated_data.pop('details')
        offer = Offer.objects.create(**validated_data)
        for detail in details_data:
            OfferDetail.objects.create(offer=offer, **detail)
        return offer

    def update(self, instance, validated_data):
        """Updates an offer and its details."""
        details_data = validated_data.pop('details', None)
        instance = self._update_offer_fields(instance, validated_data)
        if details_data:
            self._update_details(instance, details_data)
        return instance

    def _update_offer_fields(self, instance, validated_data):
        """Updates the main offer fields."""
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance

    def _update_details(self, instance, details_data):
        """Updates offer details by offer_type."""
        for detail in details_data:
            offer_type = detail.get('offer_type')
            OfferDetail.objects.filter(
                offer=instance,
                offer_type=offer_type
            ).update(**detail)


class OfferListSerializer(OfferMinValuesMixin, serializers.ModelSerializer):
    """Serializer for listing offers with computed fields."""
    details = OfferDetailUrlSerializer(many=True, read_only=True)
    min_price = serializers.SerializerMethodField()
    min_delivery_time = serializers.SerializerMethodField()
    user_details = serializers.SerializerMethodField()

    class Meta:
        model = Offer
        fields = [
            'id',
            'user',
            'title',
            'image',
            'description',
            'created_at',
            'updated_at',
            'details',
            'min_price',
            'min_delivery_time',
            'user_details'
        ]

    def get_user_details(self, obj):
        """Returns basic user details of the offer creator."""
        return {
            'first_name': obj.user.first_name,
            'last_name': obj.user.last_name,
            'username': obj.user.username
        }


class OfferRetrieveSerializer(OfferMinValuesMixin, serializers.ModelSerializer):
    """Serializer for retrieving a single offer with detail urls."""
    details = OfferDetailUrlSerializer(many=True, read_only=True)
    min_price = serializers.SerializerMethodField()
    min_delivery_time = serializers.SerializerMethodField()

    class Meta:
        model = Offer
        fields = [
            'id',
            'user',
            'title',
            'image',
            'description',
            'created_at',
            'updated_at',
            'details',
            'min_price',
            'min_delivery_time'
        ]