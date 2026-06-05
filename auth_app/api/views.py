# Third-party imports
from django.contrib.auth import authenticate
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

# Local imports
from .serializers import LoginSerializer, RegistrationSerializer


class RegistrationView(APIView):
    """View to handle user registration."""
    permission_classes = [AllowAny]

    def post(self, request):
        """Processes the POST request to register a user."""
        serializer = RegistrationSerializer(data=request.data)
        
        if serializer.is_valid():
            user = serializer.save()
            token, _ = Token.objects.get_or_create(user=user)
            
            return Response({
                "token": token.key,
                "username": user.username,
                "email": user.email,
                "user_id": user.id
            }, status=status.HTTP_201_CREATED)
            
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    
class LoginView(APIView):
    """View to handle user login."""
    permission_classes = [AllowAny]

    def post(self, request):
        """Processes POST request to authenticate a user."""
        serializer = LoginSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        user = authenticate(
            username=serializer.validated_data['username'],
            password=serializer.validated_data['password']
        )

        if not user:
            return Response(
                {"error": "Invalid credentials."},
                status=status.HTTP_400_BAD_REQUEST
            )

        token, _ = Token.objects.get_or_create(user=user)

        return Response({
            "token": token.key,
            "username": user.username,
            "email": user.email,
            "user_id": user.id
        }, status=status.HTTP_200_OK)