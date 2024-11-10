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
@admin.register(UserAddresses)
class AddressAdmin(admin.ModelAdmin):
    # Fields to be displayed in the list view
    list_display = ('user', 'name', 'phone_number', 'city', 'state', 'pincode', 'is_active')
    
    # Search functionality
    search_fields = ['user__email', 'phone_number', 'house_name', 'city', 'state', 'pincode']
    
    # Filtering options in the admin panel
    list_filter = ('is_active', 'state', 'city')
    
    # Fields to display for the form when adding or editing an address
    fields = ('user', 'name', 'house_name', 'street_name_1', 'street_name_2', 'city', 'state', 'pincode', 'phone_number', 'is_active')
    