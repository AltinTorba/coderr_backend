# Third-party imports
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework.authtoken.models import Token

# Local imports
from auth_app.models import CustomUser
from profiles_app.models import UserProfile


class ProfileRetrieveTests(APITestCase):
    """Tests for GET /api/profile/{pk}/ endpoint."""

    def setUp(self):
        """Create test user with profile and token."""
        self.user = CustomUser.objects.create_user(
            username="testuser",
            email="test@test.com",
            password="test123",
            type="customer"
        )
        self.profile = UserProfile.objects.create(user=self.user)
        self.profile.location = "Berlin"
        self.profile.tel = "123456789"
        self.profile.description = "Test description"
        self.profile.working_hours = "9-17"
        self.profile.save()
        
        self.token = Token.objects.create(user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.token.key}')
        self.url = f'/api/profile/{self.user.id}/'

    def test_profile_retrieve_success(self):
        """Test successful retrieval of user profile."""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['username'], self.user.username)
        self.assertEqual(response.data['location'], 'Berlin')

    def test_profile_retrieve_unauthenticated(self):
        """Test profile retrieval fails without authentication."""
        self.client.credentials()
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class ProfileUpdateTests(APITestCase):
    """Tests for PATCH /api/profile/{pk}/ endpoint."""

    def setUp(self):
        """Create test user with profile and token."""
        self.user = CustomUser.objects.create_user(
            username="testuser",
            email="test@test.com",
            password="test123",
            type="customer"
        )
        UserProfile.objects.create(user=self.user)
        self.token = Token.objects.create(user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.token.key}')
        self.url = f'/api/profile/{self.user.id}/'
        self.update_data = {
            "location": "Munich",
            "tel": "987654321",
            "description": "Updated description"
        }

    def test_profile_update_success(self):
        """Test successful profile update by owner."""
        response = self.client.patch(self.url, self.update_data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['location'], 'Munich')

    def test_profile_update_not_owner(self):
        """Test profile update fails if not owner."""
        other_user = CustomUser.objects.create_user(
            username="otheruser",
            email="other@test.com",
            password="test123",
            type="customer"
        )
        UserProfile.objects.create(user=other_user)
        other_token = Token.objects.create(user=other_user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {other_token.key}')
        
        response = self.client.patch(self.url, self.update_data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class BusinessProfileListTests(APITestCase):
    """Tests for GET /api/profiles/business/ endpoint."""

    def setUp(self):
        """Create business users."""
        self.business_user = CustomUser.objects.create_user(
            username="business",
            email="business@test.com",
            password="test123",
            type="business"
        )
        self.profile = UserProfile.objects.create(
            user=self.business_user,
            location="Berlin"
        )
        
        self.token = Token.objects.create(user=self.business_user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.token.key}')
        self.url = '/api/profiles/business/'

    def test_business_list_success(self):
        """Test successful retrieval of business profiles."""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsInstance(response.data, list)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['type'], 'business')

    def test_business_list_unauthenticated(self):
        """Test business list fails without authentication."""
        self.client.credentials()
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class CustomerProfileListTests(APITestCase):
    """Tests for GET /api/profiles/customer/ endpoint."""

    def setUp(self):
        """Create customer users."""
        self.customer_user = CustomUser.objects.create_user(
            username="customer",
            email="customer@test.com",
            password="test123",
            type="customer"
        )
        UserProfile.objects.create(user=self.customer_user)
        self.token = Token.objects.create(user=self.customer_user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.token.key}')
        self.url = '/api/profiles/customer/'

    def test_customer_list_success(self):
        """Test successful retrieval of customer profiles."""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsInstance(response.data, list)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['type'], 'customer')

    def test_customer_list_unauthenticated(self):
        """Test customer list fails without authentication."""
        self.client.credentials()
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)