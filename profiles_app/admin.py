# Third-party imports
from django.contrib import admin

# Local
from .models import UserProfile

admin.site.register(UserProfile)