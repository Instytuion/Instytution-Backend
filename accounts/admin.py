from django.contrib import admin

from .models import CustomUser,Whishlists

@admin.register(CustomUser)
class CustomUserAdmin(admin.ModelAdmin):
    list_display = ('id', 'email', 'first_name', 'last_name', 'role', 'is_active', 'register_mode', 'created_at', 'updated_at')
    search_fields = ('email', 'first_name', 'last_name')
@admin.register(Whishlists)

class WhishlistAdmin(admin.ModelAdmin):
    list_display = ('user', 'product', )
    search_fields = ('user', 'product')