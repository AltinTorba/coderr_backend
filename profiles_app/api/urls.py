# Third-party imports
from django.urls import path

# Local imports
from .views import (
    BusinessProfileListView,
    CustomerProfileListView,
    ProfileView,
)

urlpatterns = [
    path('profile/<int:pk>/', ProfileView.as_view(), name='profile'),
    path('profiles/business/', BusinessProfileListView.as_view(), name='business-list'),
    path('profiles/customer/', CustomerProfileListView.as_view(), name='customer-list'),
]