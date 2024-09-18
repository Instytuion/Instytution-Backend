from django.contrib import admin

from .models import CustomUser

@admin.register(CustomUser)
class CustomUserAdmin(admin.ModelAdmin):
    list_display = ('id', 'email', 'first_name', 'last_name', 'role', 'is_active', 'register_mode')
    search_fields = ('email', 'first_name', 'last_name')