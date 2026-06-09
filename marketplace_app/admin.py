# Third-party
from django.contrib import admin

# Local
from .models import Offer, OfferDetail, Order

admin.site.register(Offer)
admin.site.register(OfferDetail)
admin.site.register(Order)