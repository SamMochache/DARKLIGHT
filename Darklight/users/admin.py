from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser  # Or whatever your model is named

admin.site.register(CustomUser, UserAdmin)
