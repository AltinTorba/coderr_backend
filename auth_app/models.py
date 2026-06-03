from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):
    CUSTOMER = 'customer'
    BUSINESS = 'business'

    USER_TYPE_CHOICES = [
        (CUSTOMER, 'Customer'),
        (BUSINESS, 'Business'),
    ]

    type = models.CharField(
        max_length=20,
        choices=USER_TYPE_CHOICES,
        default=CUSTOMER
    )
    email = models.EmailField(unique=True)

    def __str__(self):
        return self.username