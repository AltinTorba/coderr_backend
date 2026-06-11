# Third-party imports
from django.contrib import admin

# Local
from .models import Review

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    """Admin configuration for Review model."""
    list_display = ['reviewer', 'business_user', 'rating']