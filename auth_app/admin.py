from django.contrib import admin
from django.contrib.auth.admin import UserAdmin


from .models import CustomUser

@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    """Admin configuration for CustomUser model."""
    list_display = [
    'username', 'email', 'first_name', 'last_name',
    'type', 'is_staff', 'date_joined'
    ]
    search_fields = ['username', 'email', 'first_name', 'last_name']
    list_filter = ['type', 'is_staff']
    fieldsets = UserAdmin.fieldsets + (
        ('Custom Fields', {'fields': ('type',)}),
    )

