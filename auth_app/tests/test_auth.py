# Third-party imports
from rest_framework import status
from rest_framework.test import APITestCase

# Local imports
from auth_app.models import CustomUser


class RegistrationTests(APITestCase):
    """Tests for the registration endpoint."""

    def setUp(self):
        """Sets test URL and valid payload."""
        self.url = '/api/registration/'
        self.valid_data = {
            'username': 'testuser',
            'email': 'test@test.com',
            'password': 'test123',
            'repeated_password': 'test123',
            'type': 'customer'
        }

    def test_registration_success(self):
        """Tests successful registration with valid data."""
        response = self.client.post(self.url, self.valid_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('token', response.data)
        self.assertIn('user_id', response.data)

    def test_registration_password_mismatch(self):
        """Tests registration fails when passwords differ."""
        self.valid_data['repeated_password'] = 'wrong123'
        response = self.client.post(self.url, self.valid_data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        
        
class LoginTests(APITestCase):
    """Tests for the login endpoint."""

    def setUp(self):
        """Create user and login payload."""
        self.url = "/api/login/"
        self.user = CustomUser.objects.create_user(
            username="testuser",
            email="test@test.com",
            password="test123",
            type="customer",
        )
        self.valid_data = {
            "username": "testuser",
            "password": "test123",
        }

    def test_login_success(self):
        """Test successful login with valid credentials."""
        response = self.client.post(self.url, self.valid_data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("token", response.data)
        self.assertEqual(response.data["username"], self.user.username)

    def test_login_invalid_credentials(self):
        """Test login fails with wrong password."""
        self.valid_data["password"] = "wrong123"
        response = self.client.post(self.url, self.valid_data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)