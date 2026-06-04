# Third-party imports
from django.urls import path

# Local imports
from .views import RegistrationView

urlpatterns = [
    path('registration/', RegistrationView.as_view(), name='registration'),
]