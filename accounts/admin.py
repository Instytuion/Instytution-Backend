from django.contrib import admin

from .models import *

@admin.register(CustomUser)
class CustomUserAdmin(admin.ModelAdmin):
    list_display = ('id', 'email', 'first_name', 'last_name', 'role', 'is_active', 'register_mode', 'created_at', 'updated_at')
    search_fields = ('email', 'first_name', 'last_name')
@admin.register(Whishlists)

class WhishlistAdmin(admin.ModelAdmin):
    list_display = ('user', 'product', )
    search_fields = ('user', 'product')
    
@admin.register(CartItem)
class CartItem(admin.ModelAdmin):
    list_display = ( 'id','product', 'quantity', 'cart__user__email')
    search_fields = ( 'product',)
    list_filter = ( 'product', 'quantity',)

@admin.register(Cart)
class Cart(admin.ModelAdmin):
    list_display = ('user', )
    search_fields = ('user',)
    list_filter = ('user',)


@admin.register(Rating)
class RatingAdmin(admin.ModelAdmin):
    list_display = ('user', 'product', 'rating', 'feedback', 'created_at')  
    list_filter = ('product',)  
    search_fields = ('user__username', 'product__name')  

@admin.register(RatingImage)
class RatingImageAdmin(admin.ModelAdmin):
    list_display = ('id', 'rating', 'image')