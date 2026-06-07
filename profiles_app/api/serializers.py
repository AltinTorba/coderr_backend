# Third-party imports
from rest_framework import serializers

# Local imports
from profiles_app.models import UserProfile


class UserProfileSerializer(serializers.ModelSerializer):
    """Serializer for full profile details (GET, PATCH)."""
    username = serializers.CharField(source='user.username', read_only=True)
    first_name = serializers.CharField(source='user.first_name', read_only=True)
    last_name = serializers.CharField(source='user.last_name', read_only=True)
    email = serializers.CharField(source='user.email', read_only=True)
    type = serializers.CharField(source='user.type', read_only=True)
    user = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = UserProfile
        fields = [
            'user',
            'username',
            'first_name',
            'last_name',
            'file',
            'email',
            'type',
            'location',
            'tel',
            'description',
            'working_hours',
            'created_at'
        ]
        read_only_fields = ['created_at']


class BusinessProfileListSerializer(serializers.ModelSerializer):
    """Serializer for listing business profiles."""
    username = serializers.CharField(source='user.username', read_only=True)
    first_name = serializers.CharField(source='user.first_name', read_only=True)
    last_name = serializers.CharField(source='user.last_name', read_only=True)
    type = serializers.CharField(source='user.type', read_only=True)

    class Meta:
        model = UserProfile
        fields = [
            'user',
            'username',
            'first_name',
            'last_name',
            'file',
            'location',
            'tel',
            'description',
            'working_hours',
            'type'
        ]


class CustomerProfileListSerializer(serializers.ModelSerializer):
    """Serializer for listing customer profiles."""
    username = serializers.CharField(source='user.username', read_only=True)
    first_name = serializers.CharField(source='user.first_name', read_only=True)
    last_name = serializers.CharField(source='user.last_name', read_only=True)
    type = serializers.CharField(source='user.type', read_only=True)

    class Meta:
        model = UserProfile
        fields = [
            'user',
            'username',
            'first_name',
            'last_name',
            'file',
            'type'
        ]