# Third-party imports
from rest_framework import serializers

# Local imports
from profiles_app.models import UserProfile


class UserProfileSerializer(serializers.ModelSerializer):
    """Serializer for UserProfile with user details."""
    username = serializers.CharField(source='user.username', read_only=True)
    email = serializers.CharField(source='user.email', read_only=True)
    type = serializers.CharField(source='user.type', read_only=True)
    user = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = UserProfile
        fields = [
            'user',
            'username',
            'email',
            'type',
            'location',
            'tel',
            'description',
            'working_hours',
            'created_at'
        ]
        read_only_fields = ['created_at']


class UserProfileListSerializer(serializers.ModelSerializer):
    """Serializer for listing profiles (business/customer)."""
    username = serializers.CharField(source='user.username', read_only=True)
    type = serializers.CharField(source='user.type', read_only=True)

    class Meta:
        model = UserProfile
        fields = ['user', 'username', 'type', 'location', 'created_at']
