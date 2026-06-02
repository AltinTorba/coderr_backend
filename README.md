# Coderr Backend API

A freelance platform API where business users 
can offer services and customers can place orders.

## Tech Stack
- Python 3.x
- Django 5.x
- Django REST Framework
- SQLite (development)

## Installation

1. Clone the repository
git clone https://github.com/username/coderr-backend.git
cd coderr-backend

2. Create virtual environment
python -m venv venv
venv\Scripts\activate  # Windows
source venv/bin/activate  # Mac/Linux

3. Install dependencies
pip install -r requirements.txt

4. Create .env file
cp .env.example .env
# Fill in your values in .env

5. Run migrations
python manage.py migrate

6. Create superuser
python manage.py createsuperuser

7. Start server
python manage.py runserver

## Environment Variables
SECRET_KEY=your-secret-key
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

## API Endpoints
### Authentication
- POST /api/registration/ - Register new user
- POST /api/login/ - Login user

### Profiles
- GET /api/profile/{pk}/ - Get user profile
- PATCH /api/profile/{pk}/ - Update user profile
- GET /api/profiles/business/ - List business profiles
- GET /api/profiles/customer/ - List customer profiles

### Offers
- GET /api/offers/ - List all offers
- POST /api/offers/ - Create offer (business only)
- GET /api/offers/{id}/ - Get offer details
- PATCH /api/offers/{id}/ - Update offer
- DELETE /api/offers/{id}/ - Delete offer

### Orders
- GET /api/orders/ - List user orders
- POST /api/orders/ - Create order (customer only)
- PATCH /api/orders/{id}/ - Update order status
- DELETE /api/orders/{id}/ - Delete order (admin only)

### Reviews
- GET /api/reviews/ - List reviews
- POST /api/reviews/ - Create review (customer only)
- PATCH /api/reviews/{id}/ - Update review
- DELETE /api/reviews/{id}/ - Delete review

## Admin Panel
Access the admin panel at /admin/