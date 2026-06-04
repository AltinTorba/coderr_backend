# Third-party imports
from django.contrib import admin

# Local
from .models import CustomUser

admin.site.register(CustomUser)