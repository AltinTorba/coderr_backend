# Coderr Backend API

A freelance platform API where business users
can offer services and customers can place orders.

## Tech Stack

- Python 3.x
- Django 5.x
- Django REST Framework
- SQLite (development)

## Project Structure

- `auth_app` - Authentication (register, login)
- `profiles_app` - User profiles
- `marketplace_app` - Offers, orders, reviews
- `base_app` - Platform statistics

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

- **Business** - Can create offers, manage orders
- **Customer** - Can place orders, leave reviews

## API Endpoints

### Authentication

- `POST /api/registration/` - Register new user
- `POST /api/login/` - Login user

### Profiles

- `GET /api/profile/{pk}/` - Get user profile
- `PATCH /api/profile/{pk}/` - Update own profile
- `GET /api/profiles/business/` - List business profiles
- `GET /api/profiles/customer/` - List customer profiles

### Offers

- `GET /api/offers/` - List all offers
- `POST /api/offers/` - Create offer (business only)
- `GET /api/offers/{id}/` - Get offer details
- `PATCH /api/offers/{id}/` - Update offer (owner only)
- `DELETE /api/offers/{id}/` - Delete offer (owner only)
- `GET /api/offerdetails/{id}/` - Get offer detail

### Orders

- `GET /api/orders/` - List user orders
- `POST /api/orders/` - Create order (customer only)
- `PATCH /api/orders/{id}/` - Update order status (business only)
- `DELETE /api/orders/{id}/` - Delete order (admin only)
- `GET /api/order-count/{id}/` - Get active order count
- `GET /api/completed-order-count/{id}/` - Get completed order count

### Reviews

- `GET /api/reviews/` - List reviews
- `POST /api/reviews/` - Create review (customer only)
- `PATCH /api/reviews/{id}/` - Update review (owner only)
- `DELETE /api/reviews/{id}/` - Delete review (owner only)

### General

- `GET /api/base-info/` - Platform statistics

## Admin Panel

Access the admin panel at `/admin/`