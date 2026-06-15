from rest_framework import serializers

from profiles_app.models import UserProfile


class UserProfileSerializer(serializers.ModelSerializer):
    """Serializer for full profile details (GET, PATCH)."""
    username = serializers.CharField(source='user.username', read_only=True)
    first_name = serializers.CharField(source='user.first_name', required=False)
    last_name = serializers.CharField(source='user.last_name', required=False)
    email = serializers.CharField(source='user.email', required=False)
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

    def update(self, instance, validated_data):
        """Updates profile and nested user fields."""
        user_data = validated_data.pop('user', {})
        if user_data:
            for attr, value in user_data.items():
                setattr(instance.user, attr, value)
            instance.user.save()
        return super().update(instance, validated_data)


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
    uploaded_at = serializers.DateTimeField(source='created_at', read_only=True, format='%Y-%m-%dT%H:%M:%S')

    class Meta:
        model = UserProfile
        fields = [
            'user',
            'username',
            'first_name',
            'last_name',
            'file',
            'uploaded_at',
            'type'
        ]

