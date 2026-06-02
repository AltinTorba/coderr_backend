# Third-party
from django.contrib.auth.models import AbstractUser
from django.db import models


class CustomUser(AbstractUser):
    """
    Custom user model that extends AbstractUser.
    Adds a 'type' field to distinguish between
    customer and business users.
    """
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

    def __str__(self):
        """Returns the username as string representation."""
        return self.username
    
    
class UserProfile(models.Model):
    """
    Extended profile for each user.
    Created automatically when a user registers.
    """
    user = models.OneToOneField(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='profile'
    )
    file = models.ImageField(
        upload_to='profiles/',
        blank=True,
        null=True
    )
    location = models.CharField(max_length=100, blank=True, default='')
    tel = models.CharField(max_length=20, blank=True, default='')
    description = models.TextField(blank=True, default='')
    working_hours = models.CharField(max_length=50, blank=True, default='')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'User Profile'
        verbose_name_plural = 'User Profiles'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username} - {self.user.type}"