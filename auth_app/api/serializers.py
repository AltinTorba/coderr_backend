# Third-party imports
from rest_framework import serializers

# Local
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
        """Creates a new user with hashed password."""
        validated_data.pop('repeated_password')
        user = CustomUser.objects.create_user(**validated_data)
        UserProfile.objects.create(user=user)
        return user