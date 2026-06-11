from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.test import APITestCase

from auth_app.models import CustomUser
from base_app.models import Review
from marketplace_app.models import Offer


class ReviewBaseTests(APITestCase):
    """Base setup for review tests."""

    def setUp(self):
        """Creates users and a review for testing."""
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
        self.other_customer = CustomUser.objects.create_user(
            username='other_customer',
            email='other@test.com',
            password='test123',
            type='customer'
        )
        self.review = Review.objects.create(
            business_user=self.business_user,
            reviewer=self.customer_user,
            rating=4,
            description='Sehr gut!'
        )
        self.token = Token.objects.create(user=self.customer_user)
        self.client.credentials(
            HTTP_AUTHORIZATION=f'Token {self.token.key}'
        )
        self.url = '/api/reviews/'
        self.detail_url = f'/api/reviews/{self.review.id}/'
        self.valid_data = {
            'business_user': self.business_user.id,
            'rating': 5,
            'description': 'Sehr professionell!'
        }


class ReviewListHappyTests(ReviewBaseTests):
    """Happy path tests for GET /api/reviews/."""

    def test_review_list_success(self):
        """Test successful retrieval of reviews."""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsInstance(response.data, list)

    def test_review_list_contains_review(self):
        """Test review list contains created review."""
        response = self.client.get(self.url)
        self.assertEqual(len(response.data), 1)

    def test_review_list_filter_by_business_user(self):
        """Test reviews can be filtered by business_user_id."""
        response = self.client.get(
            self.url,
            {'business_user_id': self.business_user.id}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_review_list_filter_by_reviewer(self):
        """Test reviews can be filtered by reviewer_id."""
        response = self.client.get(
            self.url,
            {'reviewer_id': self.customer_user.id}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_review_list_filter_empty_for_unknown(self):
        """Test review filter returns empty for non-existent user."""
        response = self.client.get(
            self.url,
            {'business_user_id': 99999}
        )
        self.assertEqual(len(response.data), 0)

    def test_review_list_contains_required_fields(self):
        """Test review list items contain all required fields."""
        response = self.client.get(self.url)
        review = response.data[0]
        for field in [
            'id', 'business_user', 'reviewer',
            'rating', 'description',
            'created_at', 'updated_at'
        ]:
            self.assertIn(field, review)

    def test_review_list_ordering_by_rating(self):
        """Test reviews can be ordered by rating."""
        Review.objects.create(
            business_user=self.business_user,
            reviewer=self.other_customer,
            rating=2,
            description='Nicht so gut'
        )
        response = self.client.get(self.url, {'ordering': 'rating'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        ratings = [r['rating'] for r in response.data]
        self.assertEqual(ratings, sorted(ratings))


class ReviewListUnhappyTests(ReviewBaseTests):
    """Unhappy path tests for GET /api/reviews/."""

    def test_review_list_requires_authentication(self):
        """Test review list requires authentication."""
        self.client.credentials()
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class ReviewCreateHappyTests(ReviewBaseTests):
    """Happy path tests for POST /api/reviews/."""

    def setUp(self):
        """Uses other_customer to avoid duplicate review."""
        super().setUp()
        other_token = Token.objects.create(user=self.other_customer)
        self.client.credentials(
            HTTP_AUTHORIZATION=f'Token {other_token.key}'
        )

    def test_review_create_success(self):
        """Test successful review creation by customer."""
        response = self.client.post(
            self.url,
            self.valid_data,
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['rating'], 5)

    def test_review_create_sets_reviewer(self):
        """Test review creation sets reviewer to current user."""
        response = self.client.post(
            self.url,
            self.valid_data,
            format='json'
        )
        self.assertEqual(
            response.data['reviewer'],
            self.other_customer.id
        )

    def test_review_create_increments_count(self):
        """Test review creation increases total count."""
        initial = Review.objects.count()
        self.client.post(self.url, self.valid_data, format='json')
        self.assertEqual(Review.objects.count(), initial + 1)


class ReviewCreateUnhappyTests(ReviewBaseTests):
    """Unhappy path tests for POST /api/reviews/."""

    def test_review_create_duplicate_raises_400(self):
        """Test creating duplicate review returns 400."""
        response = self.client.post(
            self.url,
            self.valid_data,
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_review_create_forbidden_for_business(self):
        """Test review creation is forbidden for business users."""
        business_token = Token.objects.create(user=self.business_user)
        self.client.credentials(
            HTTP_AUTHORIZATION=f'Token {business_token.key}'
        )
        response = self.client.post(
            self.url,
            self.valid_data,
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_review_create_requires_authentication(self):
        """Test review creation requires authentication."""
        self.client.credentials()
        response = self.client.post(
            self.url,
            self.valid_data,
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_review_create_invalid_rating(self):
        """Test review creation fails with rating out of range."""
        other_token = Token.objects.create(user=self.other_customer)
        self.client.credentials(
            HTTP_AUTHORIZATION=f'Token {other_token.key}'
        )
        self.valid_data['rating'] = 10
        response = self.client.post(
            self.url,
            self.valid_data,
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_review_create_missing_rating(self):
        """Test review creation fails without rating field."""
        other_token = Token.objects.create(user=self.other_customer)
        self.client.credentials(
            HTTP_AUTHORIZATION=f'Token {other_token.key}'
        )
        self.valid_data.pop('rating')
        response = self.client.post(
            self.url,
            self.valid_data,
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class ReviewUpdateHappyTests(ReviewBaseTests):
    """Happy path tests for PATCH /api/reviews/{id}/."""

    def test_review_update_rating_success(self):
        """Test successful review rating update by reviewer."""
        response = self.client.patch(
            self.detail_url,
            {'rating': 5},
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['rating'], 5)

    def test_review_update_description_success(self):
        """Test successful review description update by reviewer."""
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

    def test_review_update_persists_in_db(self):
        """Test review update is saved in database."""
        self.client.patch(
            self.detail_url,
            {'rating': 5},
            format='json'
        )
        self.review.refresh_from_db()
        self.assertEqual(self.review.rating, 5)


class ReviewUpdateUnhappyTests(ReviewBaseTests):
    """Unhappy path tests for PATCH /api/reviews/{id}/."""

    def test_review_update_not_reviewer(self):
        """Test review update fails if not the reviewer."""
        other_token = Token.objects.create(user=self.other_customer)
        self.client.credentials(
            HTTP_AUTHORIZATION=f'Token {other_token.key}'
        )
        response = self.client.patch(
            self.detail_url,
            {'rating': 5},
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_review_update_invalid_rating(self):
        """Test review update fails with invalid rating."""
        response = self.client.patch(
            self.detail_url,
            {'rating': 99},
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_review_update_not_found(self):
        """Test review update returns 404 for non-existent review."""
        response = self.client.patch(
            '/api/reviews/999/',
            {'rating': 5},
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_review_update_requires_authentication(self):
        """Test review update requires authentication."""
        self.client.credentials()
        response = self.client.patch(
            self.detail_url,
            {'rating': 5},
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class ReviewDeleteHappyTests(ReviewBaseTests):
    """Happy path tests for DELETE /api/reviews/{id}/."""

    def test_review_delete_success(self):
        """Test successful review deletion by reviewer."""
        response = self.client.delete(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Review.objects.count(), 0)


class ReviewDeleteUnhappyTests(ReviewBaseTests):
    """Unhappy path tests for DELETE /api/reviews/{id}/."""

    def test_review_delete_not_reviewer(self):
        """Test review deletion fails if not the reviewer."""
        other_token = Token.objects.create(user=self.other_customer)
        self.client.credentials(
            HTTP_AUTHORIZATION=f'Token {other_token.key}'
        )
        response = self.client.delete(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_review_delete_not_found(self):
        """Test review deletion returns 404 for non-existent review."""
        response = self.client.delete('/api/reviews/999/')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_review_delete_requires_authentication(self):
        """Test review deletion requires authentication."""
        self.client.credentials()
        response = self.client.delete(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class BaseInfoHappyTests(ReviewBaseTests):
    """Happy path tests for GET /api/base-info/."""

    def setUp(self):
        """Creates offer for base-info statistics."""
        super().setUp()
        self.offer = Offer.objects.create(
            user=self.business_user,
            title='Test Offer',
            description='Test Description'
        )

    def test_base_info_success(self):
        """Test successful retrieval of platform statistics."""
        self.client.credentials()
        response = self.client.get('/api/base-info/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_base_info_no_auth_required(self):
        """Test base-info works without authentication."""
        self.client.credentials()
        response = self.client.get('/api/base-info/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_base_info_contains_required_fields(self):
        """Test base-info contains all required fields."""
        response = self.client.get('/api/base-info/')
        for field in [
            'review_count',
            'average_rating',
            'business_profile_count',
            'offer_count'
        ]:
            self.assertIn(field, response.data)

    def test_base_info_review_count_correct(self):
        """Test review_count reflects actual review count."""
        response = self.client.get('/api/base-info/')
        self.assertEqual(
            response.data['review_count'],
            Review.objects.count()
        )

    def test_base_info_offer_count_correct(self):
        """Test offer_count reflects actual offer count."""
        response = self.client.get('/api/base-info/')
        self.assertEqual(
            response.data['offer_count'],
            Offer.objects.count()
        )

    def test_base_info_average_rating_correct(self):
        """Test average_rating is correctly calculated."""
        response = self.client.get('/api/base-info/')
        self.assertEqual(float(response.data['average_rating']), 4.0)

    def test_base_info_business_profile_count_correct(self):
        """Test business_profile_count reflects business users."""
        response = self.client.get('/api/base-info/')
        expected = CustomUser.objects.filter(type='business').count()
        self.assertEqual(
            response.data['business_profile_count'],
            expected
        )

