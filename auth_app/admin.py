# Third-party imports
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin


# Local
from .models import CustomUser

@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    """Admin configuration for CustomUser model."""
    list_display = ['username', 'email', 'type', 'is_staff']
    list_filter = ['type', 'is_staff']
    fieldsets = UserAdmin.fieldsets + (
        ('Custom Fields', {'fields': ('type',)}),
    )