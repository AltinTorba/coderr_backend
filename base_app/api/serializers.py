# Third-party imports
from rest_framework import serializers

# Local imports
from base_app.models import Review


class ReviewSerializer(serializers.ModelSerializer):
    """Serializer for reading and creating reviews."""

    class Meta:
        model = Review
        fields = [
            'id',
            'business_user',
            'reviewer',
            'rating',
            'description',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ['reviewer', 'created_at', 'updated_at']

    def validate_rating(self, value):
        """Validates that rating is between 1 and 5."""
        if value < 1 or value > 5:
            raise serializers.ValidationError(
                "Rating must be between 1 and 5."
            )
        return value

    def validate(self, attrs):
        """Validates that reviewer is not reviewing themselves."""
        request = self.context.get('request')
        if request and attrs.get('business_user') == request.user:
            raise serializers.ValidationError(
                "You cannot review yourself."
            )
        return attrs

    def create(self, validated_data):
        """Creates review with reviewer set to current user."""
        request = self.context.get('request')
        validated_data['reviewer'] = request.user
        return super().create(validated_data)


class ReviewUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating only rating and description."""

    class Meta:
        model = Review
        fields = [
            'id',
            'business_user',
            'reviewer',
            'rating',
            'description',
            'created_at',
            'updated_at'
        ]
        read_only_fields = [
            'business_user',
            'reviewer',
            'created_at',
            'updated_at'
        ]

    def validate_rating(self, value):
        """Validates that rating is between 1 and 5."""
        if value < 1 or value > 5:
            raise serializers.ValidationError(
                "Rating must be between 1 and 5."
            )
        return value


class BaseInfoSerializer(serializers.Serializer):
    """Serializer for platform statistics."""
    review_count = serializers.IntegerField()
    average_rating = serializers.FloatField()
    business_profile_count = serializers.IntegerField()
    offer_count = serializers.IntegerField()