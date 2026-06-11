from rest_framework import serializers

from auth_app.models import CustomUser
from profiles_app.models import UserProfile


class RegistrationSerializer(serializers.ModelSerializer):
    """Serializer for user registration."""
    repeated_password = serializers.CharField(write_only=True)

    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'password', 'repeated_password', 'type']
        extra_kwargs = {
            'password': {'write_only': True}
        }

    def validate(self, attrs):
        """Validates that both passwords match."""
        if attrs['password'] != attrs['repeated_password']:
            raise serializers.ValidationError({"error": "Passwords do not match."})
        return attrs

    def create(self, validated_data):
        """Creates new user with hashed password and blank profile."""
        validated_data.pop('repeated_password')
        user = CustomUser.objects.create_user(**validated_data)
        UserProfile.objects.get_or_create(user=user)
        return user
    
class LoginSerializer(serializers.Serializer):
    """Serializer for user login."""
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)

