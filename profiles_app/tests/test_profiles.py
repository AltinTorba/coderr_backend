from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.test import APITestCase

from auth_app.models import CustomUser
from profiles_app.models import UserProfile


class ProfileRetrieveHappyTests(APITestCase):
    """Happy path tests for GET /api/profile/{pk}/ endpoint."""

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
        self.assertIn('first_name', response.data)
        self.assertIn('last_name', response.data)
        self.assertIn('file', response.data)
        self.assertIn('email', response.data)


class ProfileRetrieveUnhappyTests(APITestCase):
    """Unhappy path tests for GET /api/profile/{pk}/ endpoint."""

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
        self.url = f'/api/profile/{self.user.id}/'

    def test_profile_retrieve_unauthenticated(self):
        """Test profile retrieval fails without authentication."""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        
    def test_profile_retrieve_not_found(self):
        """Test profile retrieval returns 404 for non-existent profile."""
        token, _ = Token.objects.get_or_create(user=self.user)
        self.client.credentials(
            HTTP_AUTHORIZATION=f'Token {token.key}'
        )
        response = self.client.get('/api/profile/999/')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class ProfileUpdateHappyTests(APITestCase):
    """Happy path tests for PATCH /api/profile/{pk}/ endpoint."""

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

    def test_profile_update_success(self):
        """Test successful profile update by owner."""
        response = self.client.patch(self.url, {"location": "Munich"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['location'], 'Munich')



class ProfileUpdateUnhappyTests(APITestCase):
    """Unhappy path tests for PATCH /api/profile/{pk}/ endpoint."""

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
        self.url = f'/api/profile/{self.user.id}/'

    def test_profile_update_unauthenticated(self):
        """Test profile update fails without authentication."""
        response = self.client.patch(self.url, {"location": "Munich"})
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

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
        self.client.credentials(
            HTTP_AUTHORIZATION=f'Token {other_token.key}'
        )
        response = self.client.patch(self.url, {"location": "Munich"})
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_profile_update_not_found(self):
        """Test profile update returns 404 for non-existent profile."""
        token, _ = Token.objects.get_or_create(user=self.user)
        self.client.credentials(
            HTTP_AUTHORIZATION=f'Token {token.key}'
        )
        response = self.client.patch('/api/profile/999/', {})
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class BusinessProfileListHappyTests(APITestCase):
    """Happy path tests for GET /api/profiles/business/ endpoint."""

    def setUp(self):
        """Create business user with profile and token."""
        self.business_user = CustomUser.objects.create_user(
            username="business",
            email="business@test.com",
            password="test123",
            type="business"
        )
        UserProfile.objects.create(
            user=self.business_user,
            location="Berlin"
        )
        self.token = Token.objects.create(user=self.business_user)
        self.client.credentials(
            HTTP_AUTHORIZATION=f'Token {self.token.key}'
        )
        self.url = '/api/profiles/business/'

    def test_business_list_success(self):
        """Test successful retrieval of business profiles."""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsInstance(response.data, list)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['type'], 'business')
        self.assertIn('first_name', response.data[0])
        self.assertIn('last_name', response.data[0])
        self.assertIn('file', response.data[0])


class BusinessProfileListUnhappyTests(APITestCase):
    """Unhappy path tests for GET /api/profiles/business/ endpoint."""

    def setUp(self):
        """Create business user."""
        self.url = '/api/profiles/business/'

    def test_business_list_unauthenticated(self):
        """Test business list fails without authentication."""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class CustomerProfileListHappyTests(APITestCase):
    """Happy path tests for GET /api/profiles/customer/ endpoint."""

    def setUp(self):
        """Create customer user with profile and token."""
        self.customer_user = CustomUser.objects.create_user(
            username="customer",
            email="customer@test.com",
            password="test123",
            type="customer"
        )
        UserProfile.objects.create(user=self.customer_user)
        self.token = Token.objects.create(user=self.customer_user)
        self.client.credentials(
            HTTP_AUTHORIZATION=f'Token {self.token.key}'
        )
        self.url = '/api/profiles/customer/'

    def test_customer_list_success(self):
        """Test successful retrieval of customer profiles."""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsInstance(response.data, list)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['type'], 'customer')
        self.assertIn('first_name', response.data[0])
        self.assertIn('last_name', response.data[0])
        self.assertIn('file', response.data[0])


class CustomerProfileListUnhappyTests(APITestCase):
    """Unhappy path tests for GET /api/profiles/customer/ endpoint."""

    def setUp(self):
        """Sets up URL."""
        self.url = '/api/profiles/customer/'

    def test_customer_list_unauthenticated(self):
        """Test customer list fails without authentication."""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class ProfileAutoCreateTests(APITestCase):
    """Tests that UserProfile is created automatically on registration."""

    def test_profile_created_on_registration(self):
        """Test UserProfile exists after API registration."""
        data = {
            'username': 'newuser',
            'email': 'newuser@test.com',
            'password': 'test123',
            'repeated_password': 'test123',
            'type': 'customer'
        }
        self.client.post('/api/registration/', data)
        self.assertTrue(
            UserProfile.objects.filter(
                user__username='newuser'
            ).exists()
        )

