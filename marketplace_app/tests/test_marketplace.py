from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.test import APITestCase

from auth_app.models import CustomUser
from marketplace_app.models import Offer, OfferDetail, Order


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
    """Happy path tests for GET /api/offers/."""

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
        response = self.client.get(self.url, {'creator_id': 99999})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 0)

    def test_offer_list_contains_user_details(self):
        """Test offer list contains user_details field."""
        response = self.client.get(self.url)
        result = response.data['results'][0]
        self.assertIn('user_details', result)
        self.assertIn('username', result['user_details'])
        self.assertIn('first_name', result['user_details'])
        self.assertIn('last_name', result['user_details'])

    def test_offer_list_details_have_url(self):
        """Test each detail in list has id and url fields."""
        response = self.client.get(self.url)
        detail = response.data['results'][0]['details'][0]
        self.assertIn('id', detail)
        self.assertIn('url', detail)

class OfferCreateHappyTests(OfferBaseTests):
    """Happy path tests for POST /api/offers/."""

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

    def test_offer_create_sets_correct_user(self):
        """Test offer creation assigns correct user."""
        response = self.client.post(
            self.url,
            self.valid_data,
            format='json'
        )
        self.assertEqual(
            response.data['user'],
            self.business_user.id
        )


class OfferCreateUnhappyTests(OfferBaseTests):
    """Unhappy path tests for POST /api/offers/."""

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

    def test_offer_create_missing_title(self):
        """Test offer creation fails without title."""
        self.valid_data.pop('title')
        response = self.client.post(
            self.url,
            self.valid_data,
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class OfferRetrieveHappyTests(OfferBaseTests):
    """Happy path tests for GET /api/offers/{id}/."""

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

    def test_offer_retrieve_contains_min_price(self):
        """Test offer retrieve contains min_price field."""
        response = self.client.get(self.detail_url)
        self.assertIn('min_price', response.data)

    def test_offer_retrieve_contains_min_delivery_time(self):
        """Test offer retrieve contains min_delivery_time field."""
        response = self.client.get(self.detail_url)
        self.assertIn('min_delivery_time', response.data)


class OfferRetrieveUnhappyTests(OfferBaseTests):
    """Unhappy path tests for GET /api/offers/{id}/."""

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
    """Happy path tests for PATCH /api/offers/{id}/."""

    def test_offer_update_success(self):
        """Test successful offer update by owner."""
        response = self.client.patch(
            self.detail_url,
            {'title': 'Updated Title'},
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], 'Updated Title')

    def test_offer_update_detail_price(self):
        """Test successful update of offer detail price by owner."""
        response = self.client.patch(
            self.detail_url,
            {
                'details': [
                    {'offer_type': 'basic', 'price': 150}
                ]
            },
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        updated = OfferDetail.objects.get(
            offer=self.offer,
            offer_type='basic'
        )
        self.assertEqual(float(updated.price), 150.0)

    def test_offer_update_description(self):
        """Test successful update of offer description."""
        response = self.client.patch(
            self.detail_url,
            {'description': 'Updated description'},
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.data['description'],
            'Updated description'
        )


class OfferUpdateUnhappyTests(OfferBaseTests):
    """Unhappy path tests for PATCH /api/offers/{id}/."""

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
    """Happy path tests for DELETE /api/offers/{id}/."""

    def test_offer_delete_success(self):
        """Test successful offer deletion by owner."""
        response = self.client.delete(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Offer.objects.count(), 0)


class OfferDeleteUnhappyTests(OfferBaseTests):
    """Unhappy path tests for DELETE /api/offers/{id}/."""

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
    """Happy path tests for GET /api/offerdetails/{id}/."""

    def setUp(self):
        super().setUp()
        self.offer_detail = self.offer.details.get(offer_type='basic')
        self.offer_detail_url = (
            f'/api/offerdetails/{self.offer_detail.id}/'
        )

    def test_offer_detail_retrieve_success(self):
        """Test successful retrieval of offer detail."""
        response = self.client.get(self.offer_detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['offer_type'], 'basic')
        self.assertEqual(float(response.data['price']), 100.0)

    def test_offer_detail_retrieve_fields(self):
        """Test offer detail response contains all required fields."""
        response = self.client.get(self.offer_detail_url)
        for field in [
            'id', 'title', 'revisions',
            'delivery_time_in_days', 'price',
            'features', 'offer_type'
        ]:
            self.assertIn(field, response.data)


class OfferDetailRetrieveUnhappyTests(OfferBaseTests):
    """Unhappy path tests for GET /api/offerdetails/{id}/."""

    def setUp(self):
        super().setUp()
        self.offer_detail = self.offer.details.get(offer_type='basic')
        self.offer_detail_url = (
            f'/api/offerdetails/{self.offer_detail.id}/'
        )

    def test_offer_detail_retrieve_not_found(self):
        """Test offer detail retrieval returns 404 for non-existent."""
        response = self.client.get('/api/offerdetails/999/')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_offer_detail_retrieve_requires_authentication(self):
        """Test offer detail retrieval requires authentication."""
        self.client.credentials()
        response = self.client.get(self.offer_detail_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class OrderBaseTests(APITestCase):
    """Base setup for order tests."""

    def setUp(self):
        """Creates users, offer, offer_detail and order."""
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
        self.offer_detail = OfferDetail.objects.create(
            offer=self.offer,
            title='Basic',
            revisions=2,
            delivery_time_in_days=5,
            price=100,
            features=['Logo'],
            offer_type='basic'
        )
        self.order = Order.objects.create(
            customer_user=self.customer_user,
            business_user=self.business_user,
            title='Basic',
            revisions=2,
            delivery_time_in_days=5,
            price=100,
            features=['Logo'],
            offer_type='basic',
            status=Order.IN_PROGRESS
        )
        self.token = Token.objects.create(user=self.customer_user)
        self.client.credentials(
            HTTP_AUTHORIZATION=f'Token {self.token.key}'
        )
        self.url = '/api/orders/'
        self.detail_url = f'/api/orders/{self.order.id}/'


class OrderListHappyTests(OrderBaseTests):
    """Happy path tests for GET /api/orders/."""

    def test_order_list_success(self):
        """Test successful retrieval of orders for authenticated user."""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsInstance(response.data, list)

    def test_order_list_shows_only_user_orders(self):
        """Test order list shows only orders for current user."""
        response = self.client.get(self.url)
        self.assertEqual(len(response.data), 1)

    def test_order_list_contains_required_fields(self):
        """Test order list items contain required fields."""
        response = self.client.get(self.url)
        order = response.data[0]
        for field in [
            'id', 'customer_user', 'business_user',
            'title', 'status', 'price'
        ]:
            self.assertIn(field, order)

    def test_order_list_business_user_sees_own_orders(self):
        """Test business user sees orders where they are business_user."""
        business_token = Token.objects.create(user=self.business_user)
        self.client.credentials(
            HTTP_AUTHORIZATION=f'Token {business_token.key}'
        )
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)


class OrderListUnhappyTests(OrderBaseTests):
    """Unhappy path tests for GET /api/orders/."""

    def test_order_list_requires_authentication(self):
        """Test order list requires authentication."""
        self.client.credentials()
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class OrderCreateHappyTests(OrderBaseTests):
    """Happy path tests for POST /api/orders/."""

    def test_order_create_success(self):
        """Test successful order creation by customer."""
        response = self.client.post(
            self.url,
            {'offer_detail_id': self.offer_detail.id},
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['status'], Order.IN_PROGRESS)
        self.assertEqual(response.data['title'], 'Basic')

    def test_order_create_sets_correct_price(self):
        """Test order creation copies price from offer detail."""
        response = self.client.post(
            self.url,
            {'offer_detail_id': self.offer_detail.id},
            format='json'
        )
        self.assertEqual(float(response.data['price']), 100.0)

    def test_order_create_sets_correct_business_user(self):
        """Test order creation assigns correct business user."""
        response = self.client.post(
            self.url,
            {'offer_detail_id': self.offer_detail.id},
            format='json'
        )
        self.assertEqual(
            response.data['business_user'],
            self.business_user.id
        )

    def test_order_create_increments_count(self):
        """Test order creation increases total order count."""
        initial_count = Order.objects.count()
        self.client.post(
            self.url,
            {'offer_detail_id': self.offer_detail.id},
            format='json'
        )
        self.assertEqual(Order.objects.count(), initial_count + 1)


class OrderCreateUnhappyTests(OrderBaseTests):
    """Unhappy path tests for POST /api/orders/."""

    def test_order_create_forbidden_for_business(self):
        """Test order creation is forbidden for business users."""
        business_token = Token.objects.create(user=self.business_user)
        self.client.credentials(
            HTTP_AUTHORIZATION=f'Token {business_token.key}'
        )
        response = self.client.post(
            self.url,
            {'offer_detail_id': self.offer_detail.id},
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_order_create_invalid_offer_detail(self):
        """Test order creation fails with invalid offer_detail_id."""
        response = self.client.post(
            self.url,
            {'offer_detail_id': 99999},
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_order_create_requires_authentication(self):
        """Test order creation requires authentication."""
        self.client.credentials()
        response = self.client.post(
            self.url,
            {'offer_detail_id': self.offer_detail.id},
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_order_create_missing_offer_detail_id(self):
        """Test order creation fails without offer_detail_id."""
        response = self.client.post(self.url, {}, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class OrderUpdateHappyTests(OrderBaseTests):
    """Happy path tests for PATCH /api/orders/{id}/."""

    def test_order_update_status_to_completed(self):
        """Test successful order status update to completed."""
        business_token = Token.objects.create(user=self.business_user)
        self.client.credentials(
            HTTP_AUTHORIZATION=f'Token {business_token.key}'
        )
        response = self.client.patch(
            self.detail_url,
            {'status': 'completed'},
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], 'completed')

    def test_order_update_status_to_cancelled(self):
        """Test successful order status update to cancelled."""
        business_token = Token.objects.create(user=self.business_user)
        self.client.credentials(
            HTTP_AUTHORIZATION=f'Token {business_token.key}'
        )
        response = self.client.patch(
            self.detail_url,
            {'status': 'cancelled'},
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], 'cancelled')

    def test_order_update_persists_in_db(self):
        """Test order status update is saved in database."""
        business_token = Token.objects.create(user=self.business_user)
        self.client.credentials(
            HTTP_AUTHORIZATION=f'Token {business_token.key}'
        )
        self.client.patch(
            self.detail_url,
            {'status': 'completed'},
            format='json'
        )
        self.order.refresh_from_db()
        self.assertEqual(self.order.status, Order.COMPLETED)


class OrderUpdateUnhappyTests(OrderBaseTests):
    """Unhappy path tests for PATCH /api/orders/{id}/."""

    def test_order_update_forbidden_for_customer(self):
        """Test order status update is forbidden for customer."""
        response = self.client.patch(
            self.detail_url,
            {'status': 'completed'},
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_order_update_invalid_status(self):
        """Test order update fails with invalid status value."""
        business_token = Token.objects.create(user=self.business_user)
        self.client.credentials(
            HTTP_AUTHORIZATION=f'Token {business_token.key}'
        )
        response = self.client.patch(
            self.detail_url,
            {'status': 'invalid_status'},
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_order_update_requires_authentication(self):
        """Test order update requires authentication."""
        self.client.credentials()
        response = self.client.patch(
            self.detail_url,
            {'status': 'completed'},
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_order_update_not_found(self):
        """Test order update returns 404 for non-existent order."""
        business_token = Token.objects.create(user=self.business_user)
        self.client.credentials(
            HTTP_AUTHORIZATION=f'Token {business_token.key}'
        )
        response = self.client.patch(
            '/api/orders/999/',
            {'status': 'completed'},
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class OrderDeleteHappyTests(OrderBaseTests):
    """Happy path tests for DELETE /api/orders/{id}/."""

    def test_order_delete_success_by_admin(self):
        """Test successful order deletion by admin user."""
        admin = CustomUser.objects.create_superuser(
            username='admin',
            email='admin@test.com',
            password='test123'
        )
        admin_token = Token.objects.create(user=admin)
        self.client.credentials(
            HTTP_AUTHORIZATION=f'Token {admin_token.key}'
        )
        response = self.client.delete(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Order.objects.count(), 0)


class OrderDeleteUnhappyTests(OrderBaseTests):
    """Unhappy path tests for DELETE /api/orders/{id}/."""

    def test_order_delete_forbidden_for_customer(self):
        """Test order deletion is forbidden for customer."""
        response = self.client.delete(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_order_delete_forbidden_for_business(self):
        """Test order deletion is forbidden for business user."""
        business_token = Token.objects.create(user=self.business_user)
        self.client.credentials(
            HTTP_AUTHORIZATION=f'Token {business_token.key}'
        )
        response = self.client.delete(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_order_delete_requires_authentication(self):
        """Test order deletion requires authentication."""
        self.client.credentials()
        response = self.client.delete(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_order_delete_not_found(self):
        """Test order deletion returns 404 for non-existent order."""
        admin = CustomUser.objects.create_superuser(
            username='admin',
            email='admin@test.com',
            password='test123'
        )
        admin_token = Token.objects.create(user=admin)
        self.client.credentials(
            HTTP_AUTHORIZATION=f'Token {admin_token.key}'
        )
        response = self.client.delete('/api/orders/999/')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class OrderCountHappyTests(OrderBaseTests):
    """Happy path tests for GET /api/order-count/{business_user_id}/."""

    def test_order_count_success(self):
        """Test successful retrieval of in_progress order count."""
        response = self.client.get(
            f'/api/order-count/{self.business_user.id}/'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['order_count'], 1)

    def test_order_count_zero_for_no_orders(self):
        """Test order count returns 0 when no in_progress orders."""
        self.order.status = Order.COMPLETED
        self.order.save()
        response = self.client.get(
            f'/api/order-count/{self.business_user.id}/'
        )
        self.assertEqual(response.data['order_count'], 0)


class OrderCountUnhappyTests(OrderBaseTests):
    """Unhappy path tests for GET /api/order-count/{business_user_id}/."""

    def test_order_count_requires_authentication(self):
        """Test order count requires authentication."""
        self.client.credentials()
        response = self.client.get(
            f'/api/order-count/{self.business_user.id}/'
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class CompletedOrderCountHappyTests(OrderBaseTests):
    """Happy path tests for GET /api/completed-order-count/{id}/."""

    def setUp(self):
        """Creates a completed order in addition to base setup."""
        super().setUp()
        Order.objects.create(
            customer_user=self.customer_user,
            business_user=self.business_user,
            title='Basic',
            revisions=2,
            delivery_time_in_days=5,
            price=100,
            features=['Logo'],
            offer_type='basic',
            status=Order.COMPLETED
        )

    def test_completed_order_count_success(self):
        """Test successful retrieval of completed order count."""
        response = self.client.get(
            f'/api/completed-order-count/{self.business_user.id}/'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['completed_order_count'], 1)

    def test_completed_order_count_excludes_in_progress(self):
        """Test completed count does not include in_progress orders."""
        response = self.client.get(
            f'/api/completed-order-count/{self.business_user.id}/'
        )
        self.assertEqual(response.data['completed_order_count'], 1)


class CompletedOrderCountUnhappyTests(OrderBaseTests):
    """Unhappy path tests for GET /api/completed-order-count/{id}/."""

    def test_completed_order_count_requires_authentication(self):
        """Test completed order count requires authentication."""
        self.client.credentials()
        response = self.client.get(
            f'/api/completed-order-count/{self.business_user.id}/'
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        

class OfferFilterTests(OfferBaseTests):
    """Tests for offer filtering by min_price and max_delivery_time."""

    def test_filter_by_min_price(self):
        """Test offers can be filtered by min_price."""
        response = self.client.get(self.url, {'min_price': 150})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 0)

    def test_filter_by_min_price_returns_matching(self):
        """Test min_price filter returns offers above threshold."""
        response = self.client.get(self.url, {'min_price': 50})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)

    def test_filter_by_max_delivery_time(self):
        """Test offers can be filtered by max_delivery_time."""
        response = self.client.get(self.url, {'max_delivery_time': 4})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 0)

    def test_filter_by_max_delivery_time_returns_matching(self):
        """Test max_delivery_time filter returns offers within threshold."""
        response = self.client.get(self.url, {'max_delivery_time': 5})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)

    def test_filter_by_min_price_and_max_delivery_time(self):
        """Test combined filter by min_price and max_delivery_time."""
        response = self.client.get(
            self.url,
            {'min_price': 50, 'max_delivery_time': 5}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)


class OrderCountNotFoundTests(OrderBaseTests):
    """Tests for 404 on order-count and completed-order-count."""

    def test_order_count_not_found(self):
        """Test order-count returns 404 for non-existent business user."""
        response = self.client.get('/api/order-count/99999/')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_completed_order_count_not_found(self):
        """Test completed-order-count returns 404 for non-existent user."""
        response = self.client.get('/api/completed-order-count/99999/')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

