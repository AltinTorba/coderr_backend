from django.contrib import admin

from .models import Offer, OfferDetail, Order


@admin.register(Offer)
class OfferAdmin(admin.ModelAdmin):
    """Admin configuration for Offer model."""
    list_display = ['title', 'user', 'created_at']

@admin.register(OfferDetail)
class OfferDetailAdmin(admin.ModelAdmin):
    """Admin configuration for OfferDetail model."""
    list_display = ['offer', 'offer_type', 'price']

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    """Admin configuration for Order model."""
    llist_display = [
        'id', 'title', 'customer_user', 'business_user',
        'status', 'created_at'
    ]
    list_filter = ['status']
    search_fields = ['title', 'customer_user__username']

