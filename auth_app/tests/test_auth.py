# Third-party
from django.test import TestCase
from rest_framework.test import APIClient

# Local
from auth_app.models import CustomUser, UserProfile

class RegistrationHappyTestCase(TestCase):
    """Happy path tests for registration endpoint."""
    
    def setUp(self):
        """Sets up test client and valid data before each test."""
        self.client = APIClient()
        self.url = '/api/registration/'
        self.valid_data = {
            'username': 'testuser',
            'email': 'test@test.com',
            'password': 'test123',
            'repeated_password': 'test123',
            'type': 'customer'
        }
        
    def test_registration_customer_success(self):
        """Tests successful registration of a customer user."""
        response = self.client.post(self.url, self.valid_data)

        self.assertEqual(response.status_code, 201)
        self.assertIn('token', response.data)
        self.assertIn('username', response.data)
        self.assertIn('email', response.data)
        self.assertIn('user_id', response.data)