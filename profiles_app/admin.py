from django.contrib import admin

from .models import UserProfile

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    """Admin configuration for UserProfile model."""
    list_display = [
        'user', 'location', 'tel',
        'description', 'working_hours', 'created_at'
    ]
    search_fields = ['user__username', 'location']

