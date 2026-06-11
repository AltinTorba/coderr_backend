from django.contrib import admin

from .models import Review

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    """Admin configuration for Review model."""
    list_display = [
    'reviewer', 'business_user', 'rating',
    'description', 'created_at'
    ]
    list_filter = ['rating']
    search_fields = ['reviewer__username', 'business_user__username']

