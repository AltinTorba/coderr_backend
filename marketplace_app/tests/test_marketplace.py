# Third-party
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.test import APITestCase

# Local
from auth_app.models import CustomUser
from marketplace_app.models import Offer, OfferDetail, Order, Review


class OfferCreateHappyTests(APITestCase):
    """Happy path tests for POST /api/offers/ endpoint."""

    def setUp(self):
        """Creates business user with token and valid offer data."""
        self.business_user = CustomUser.objects.create_user(
            username='business',
            email='business@test.com',
            password='test123',
            type='business'
        )
        self.token = Token.objects.create(user=self.business_user)
        self.client.credentials(
            HTTP_AUTHORIZATION=f'Token {self.token.key}'
        )
        self.url = '/api/offers/'
        self.valid_data = {
            'title': 'Test Offer',
            'description': 'Test Description',
            'details': [
                {
                    'title': 'Basic',
                    'revisions': 2,
                    'delivery_time_in_days': 5,
                    'price': '100.00',
                    'features': ['Logo'],
                    'offer_type': 'basic'
                },
                {
                    'title': 'Standard',
                    'revisions': 5,
                    'delivery_time_in_days': 7,
                    'price': '200.00',
                    'features': ['Logo', 'Banner'],
                    'offer_type': 'standard'
                },
                {
                    'title': 'Premium',
                    'revisions': 10,
                    'delivery_time_in_days': 10,
                    'price': '500.00',
                    'features': ['Logo', 'Banner', 'Flyer'],
                    'offer_type': 'premium'
                }
            ]
        }