# Third-party
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

# Local
from .models import CustomUser, UserProfile


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    """
    Admin configuration for CustomUser model.
    Extends UserAdmin to include custom fields.
    """
    list_display = ['username', 'email', 'type', 'is_staff']
    list_filter = ['type', 'is_staff']
    fieldsets = UserAdmin.fieldsets + (
        ('Custom Fields', {'fields': ('type',)}),
    )


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    """
    Admin configuration for UserProfile model.
    """
    list_display = ['user', 'location', 'tel']
    list_filter = ['user__type']