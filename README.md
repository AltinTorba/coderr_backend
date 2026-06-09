# Coderr Backend API

A freelance platform API where business users
can offer services and customers can place orders.

## Tech Stack

- Python 3.x
- Django 6.x
- Django REST Framework
- SQLite (development)

## Project Structure

- `auth_app` - Authentication (register, login)
- `profiles_app` - User profiles
- `marketplace_app` - Offers and orders
- `base_app` - Reviews and platform statistics

## Installation

1. Clone the repository

```
git clone https://github.com/username/coderr-backend.git
cd coderr-backend
```

2. Create virtual environment

```
python -m venv venv
venv\Scripts\activate  # Windows
source venv/bin/activate  # Mac/Linux
```

3. Install dependencies

```
pip install -r requirements.txt
```

4. Create .env file

```
cp .env.example .env
```

5. Run migrations

```
python manage.py migrate
```

6. Create superuser

```
python manage.py createsuperuser
```

7. Start server

```
python manage.py runserver
```

## Environment Variables

```
SECRET_KEY=your-secret-key
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
```

## User Types

| Type       | Permissions                                              |
|------------|----------------------------------------------------------|
| Business   | Can create offers, manage orders, update order status   |
| Customer   | Can place orders, leave reviews                         |

## API Endpoints

### Authentication

| Method | Endpoint                 | Description          | Auth |
|--------|--------------------------|----------------------|------|
| POST   | /api/registration/       | Register new user    | No   |
| POST   | /api/login/              | Login user           | No   |

### Profiles

| Method | Endpoint                     | Description           | Auth    |
|--------|------------------------------|-----------------------|---------|
| GET    | /api/profile/{pk}/           | Get user profile      | Yes     |
| PATCH  | /api/profile/{pk}/           | Update own profile    | Owner   |
| GET    | /api/profiles/business/      | List business profiles| Yes     |
| GET    | /api/profiles/customer/      | List customer profiles| Yes     |

### Offers

| Method | Endpoint                   | Description           | Auth     |
|--------|----------------------------|-----------------------|----------|
| GET    | /api/offers/               | List all offers       | No       |
| POST   | /api/offers/               | Create offer          | Business |
| GET    | /api/offers/{id}/          | Get offer details     | Yes      |
| PATCH  | /api/offers/{id}/          | Update offer          | Owner    |
| DELETE | /api/offers/{id}/          | Delete offer          | Owner    |
| GET    | /api/offerdetails/{id}/    | Get offer detail      | Yes      |

**Query Parameters for GET /api/offers/:**

| Parameter     | Type    | Description                              |
|---------------|---------|------------------------------------------|
| creator_id    | integer | Filter by creator                        |
| search        | string  | Search in title and description          |
| ordering      | string  | Sort by `updated_at` or `min_price`      |

### Orders

| Method | Endpoint                           | Description            | Auth      |
|--------|------------------------------------|------------------------|-----------|
| GET    | /api/orders/                       | List user orders       | Yes       |
| POST   | /api/orders/                       | Create order           | Customer  |
| PATCH  | /api/orders/{id}/                  | Update status          | Business  |
| DELETE | /api/orders/{id}/                  | Delete order           | Admin     |
| GET    | /api/order-count/{business_user_id}/       | Active order count     | Yes       |
| GET    | /api/completed-order-count/{business_user_id}/ | Completed count   | Yes       |

### Reviews

| Method | Endpoint                   | Description           | Auth      |
|--------|----------------------------|-----------------------|-----------|
| GET    | /api/reviews/              | List reviews          | Yes       |
| POST   | /api/reviews/              | Create review         | Customer  |
| PATCH  | /api/reviews/{id}/         | Update review         | Reviewer  |
| DELETE | /api/reviews/{id}/         | Delete review         | Reviewer  |

**Query Parameters for GET /api/reviews/:**

| Parameter         | Type    | Description                          |
|-------------------|---------|--------------------------------------|
| business_user_id  | integer | Filter by business user              |
| reviewer_id       | integer | Filter by reviewer                   |
| ordering          | string  | Sort by `updated_at` or `rating`     |

### General

| Method | Endpoint           | Description            | Auth |
|--------|--------------------|------------------------|------|
| GET    | /api/base-info/    | Platform statistics    | No   |

## Admin Panel

Access the admin panel at `/admin/`

## Testing

python manage.py test

python manage.py test --settings=core.test_settings
