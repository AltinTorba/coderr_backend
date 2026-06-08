# Third-party imports
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.test import APITestCase

# Local imports
from auth_app.models import CustomUser
from marketplace_app.models import Offer, OfferDetail


class OfferBaseTests(APITestCase):
    """Base setup for offer tests with business user and 3 details."""

    def setUp(self):
        """Creates business user with offer and 3 details."""
        self.business_user = CustomUser.objects.create_user(
            username='business',
            email='business@test.com',
            password='test123',
            type='business'
        )
        self.customer_user = CustomUser.objects.create_user(
            username='customer',
            email='customer@test.com',
            password='test123',
            type='customer'
        )
        self.offer = Offer.objects.create(
            user=self.business_user,
            title='Grafikdesign',
            description='Professionelles Design'
        )
        OfferDetail.objects.create(
            offer=self.offer,
            title='Basic',
            revisions=2,
            delivery_time_in_days=5,
            price=100,
            features=['Logo'],
            offer_type='basic'
        )
        OfferDetail.objects.create(
            offer=self.offer,
            title='Standard',
            revisions=5,
            delivery_time_in_days=7,
            price=200,
            features=['Logo', 'Flyer'],
            offer_type='standard'
        )
        OfferDetail.objects.create(
            offer=self.offer,
            title='Premium',
            revisions=10,
            delivery_time_in_days=10,
            price=500,
            features=['Logo', 'Flyer', 'Banner'],
            offer_type='premium'
        )
        self.token = Token.objects.create(user=self.business_user)
        self.client.credentials(
            HTTP_AUTHORIZATION=f'Token {self.token.key}'
        )
        self.url = '/api/offers/'
        self.detail_url = f'/api/offers/{self.offer.id}/'
        self.valid_data = {
            'title': 'New Offer',
            'description': 'New Description',
            'details': [
                {
                    'title': 'Basic',
                    'revisions': 2,
                    'delivery_time_in_days': 5,
                    'price': 100,
                    'features': ['Logo'],
                    'offer_type': 'basic'
                },
                {
                    'title': 'Standard',
                    'revisions': 5,
                    'delivery_time_in_days': 7,
                    'price': 200,
                    'features': ['Logo', 'Flyer'],
                    'offer_type': 'standard'
                },
                {
                    'title': 'Premium',
                    'revisions': 10,
                    'delivery_time_in_days': 10,
                    'price': 500,
                    'features': ['Logo', 'Flyer', 'Banner'],
                    'offer_type': 'premium'
                }
            ]
        }


class OfferListHappyTests(OfferBaseTests):
    """Happy path tests for GET /api/offers/ endpoint."""

    def test_offer_list_success(self):
        """Test successful retrieval of offer list without authentication."""
        self.client.credentials()
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_offer_list_is_paginated(self):
        """Test offer list response is paginated."""
        response = self.client.get(self.url)
        self.assertIn('count', response.data)
        self.assertIn('next', response.data)
        self.assertIn('results', response.data)

    def test_offer_list_contains_min_price(self):
        """Test offer list contains min_price field."""
        response = self.client.get(self.url)
        self.assertIn('min_price', response.data['results'][0])

    def test_offer_list_contains_min_delivery_time(self):
        """Test offer list contains min_delivery_time field."""
        response = self.client.get(self.url)
        self.assertIn('min_delivery_time', response.data['results'][0])

    def test_offer_list_min_price_value(self):
        """Test min_price returns the lowest price from details."""
        response = self.client.get(self.url)
        self.assertEqual(
            float(response.data['results'][0]['min_price']),
            100.0
        )

    def test_offer_list_min_delivery_time_value(self):
        """Test min_delivery_time returns the shortest delivery time."""
        response = self.client.get(self.url)
        self.assertEqual(
            response.data['results'][0]['min_delivery_time'],
            5
        )

    def test_offer_list_filter_by_creator(self):
        """Test offer list can be filtered by creator_id."""
        response = self.client.get(
            self.url,
            {'creator_id': self.business_user.id}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)

    def test_offer_list_empty_for_unknown_creator(self):
        """Test offer list returns empty for non-existent creator."""
        response = self.client.get(
            self.url,
            {'creator_id': 99999}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 0)


class OfferCreateHappyTests(OfferBaseTests):
    """Happy path tests for POST /api/offers/ endpoint."""

    def test_offer_create_success(self):
        """Test successful offer creation by business user."""
        response = self.client.post(
            self.url,
            self.valid_data,
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Offer.objects.count(), 2)

    def test_offer_create_returns_details(self):
        """Test offer creation returns details in response."""
        response = self.client.post(
            self.url,
            self.valid_data,
            format='json'
        )
        self.assertIn('details', response.data)
        self.assertEqual(len(response.data['details']), 3)


class OfferCreateUnhappyTests(OfferBaseTests):
    """Unhappy path tests for POST /api/offers/ endpoint."""

    def test_offer_create_requires_3_details(self):
        """Test offer creation fails with less than 3 details."""
        self.valid_data['details'] = self.valid_data['details'][:2]
        response = self.client.post(
            self.url,
            self.valid_data,
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_offer_create_forbidden_for_customer(self):
        """Test offer creation is forbidden for customer users."""
        customer_token = Token.objects.create(user=self.customer_user)
        self.client.credentials(
            HTTP_AUTHORIZATION=f'Token {customer_token.key}'
        )
        response = self.client.post(
            self.url,
            self.valid_data,
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_offer_create_requires_authentication(self):
        """Test offer creation requires authentication."""
        self.client.credentials()
        response = self.client.post(
            self.url,
            self.valid_data,
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class OfferRetrieveHappyTests(OfferBaseTests):
    """Happy path tests for GET /api/offers/{id}/ endpoint."""

    def test_offer_retrieve_success(self):
        """Test successful retrieval of specific offer."""
        response = self.client.get(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], 'Grafikdesign')

    def test_offer_retrieve_contains_details(self):
        """Test offer retrieve contains details with id and url."""
        response = self.client.get(self.detail_url)
        self.assertIn('details', response.data)
        self.assertIn('id', response.data['details'][0])
        self.assertIn('url', response.data['details'][0])


class OfferRetrieveUnhappyTests(OfferBaseTests):
    """Unhappy path tests for GET /api/offers/{id}/ endpoint."""

    def test_offer_retrieve_not_found(self):
        """Test offer retrieval returns 404 for non-existent offer."""
        response = self.client.get('/api/offers/999/')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_offer_retrieve_requires_authentication(self):
        """Test offer retrieval requires authentication."""
        self.client.credentials()
        response = self.client.get(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class OfferUpdateHappyTests(OfferBaseTests):
    """Happy path tests for PATCH /api/offers/{id}/ endpoint."""

    def test_offer_update_success(self):
        """Test successful offer update by owner."""
        response = self.client.patch(
            self.detail_url,
            {'title': 'Updated Title'},
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], 'Updated Title')

    def test_offer_update_detail_success(self):
        """Test successful update of offer detail by owner."""
        response = self.client.patch(
            self.detail_url,
            {
                'details': [
                    {
                        'offer_type': 'basic',
                        'price': 150
                    }
                ]
            },
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class OfferUpdateUnhappyTests(OfferBaseTests):
    """Unhappy path tests for PATCH /api/offers/{id}/ endpoint."""

    def test_offer_update_not_owner(self):
        """Test offer update fails if not owner."""
        other_business = CustomUser.objects.create_user(
            username='other_business',
            email='other@test.com',
            password='test123',
            type='business'
        )
        other_token = Token.objects.create(user=other_business)
        self.client.credentials(
            HTTP_AUTHORIZATION=f'Token {other_token.key}'
        )
        response = self.client.patch(
            self.detail_url,
            {'title': 'Updated Title'},
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_offer_update_not_found(self):
        """Test offer update returns 404 for non-existent offer."""
        response = self.client.patch(
            '/api/offers/999/',
            {'title': 'Updated Title'},
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_offer_update_requires_authentication(self):
        """Test offer update requires authentication."""
        self.client.credentials()
        response = self.client.patch(
            self.detail_url,
            {'title': 'Updated Title'},
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class OfferDeleteHappyTests(OfferBaseTests):
    """Happy path tests for DELETE /api/offers/{id}/ endpoint."""

    def test_offer_delete_success(self):
        """Test successful offer deletion by owner."""
        response = self.client.delete(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Offer.objects.count(), 0)


class OfferDeleteUnhappyTests(OfferBaseTests):
    """Unhappy path tests for DELETE /api/offers/{id}/ endpoint."""

    def test_offer_delete_not_owner(self):
        """Test offer deletion fails if not owner."""
        other_business = CustomUser.objects.create_user(
            username='other_business',
            email='other@test.com',
            password='test123',
            type='business'
        )
        other_token = Token.objects.create(user=other_business)
        self.client.credentials(
            HTTP_AUTHORIZATION=f'Token {other_token.key}'
        )
        response = self.client.delete(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_offer_delete_not_found(self):
        """Test offer deletion returns 404 for non-existent offer."""
        response = self.client.delete('/api/offers/999/')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_offer_delete_requires_authentication(self):
        """Test offer deletion requires authentication."""
        self.client.credentials()
        response = self.client.delete(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class OfferDetailRetrieveHappyTests(OfferBaseTests):
    """Happy path tests for GET /api/offerdetails/{id}/ endpoint."""

    def setUp(self):
        """Gets offer detail URL."""
        super().setUp()
        self.offer_detail = self.offer.details.get(offer_type='basic')
        self.offer_detail_url = f'/api/offerdetails/{self.offer_detail.id}/'

    def test_offer_detail_retrieve_success(self):
        """Test successful retrieval of offer detail."""
        response = self.client.get(self.offer_detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['offer_type'], 'basic')
        self.assertEqual(float(response.data['price']), 100.0)


class OfferDetailRetrieveUnhappyTests(OfferBaseTests):
    """Unhappy path tests for GET /api/offerdetails/{id}/ endpoint."""

    def setUp(self):
        """Gets offer detail URL."""
        super().setUp()
        self.offer_detail = self.offer.details.get(offer_type='basic')
        self.offer_detail_url = f'/api/offerdetails/{self.offer_detail.id}/'

    def test_offer_detail_retrieve_not_found(self):
        """Test offer detail retrieval returns 404 for non-existent detail."""
        response = self.client.get('/api/offerdetails/999/')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_offer_detail_retrieve_requires_authentication(self):
        """Test offer detail retrieval requires authentication."""
        self.client.credentials()
        response = self.client.get(self.offer_detail_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)