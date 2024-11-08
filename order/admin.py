from django.contrib import admin
from .models import Order, OrderItem

# OrderItem Inline for the Order Admin
class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0  # Number of empty forms to display by default

# Order Admin
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'status', 'total_amount', 'delivery_charge', 'created_at', 'updated_at', 'expected_delivery')
    list_filter = ('status', 'created_at', 'updated_at')
    # search_fields = ('user__email', 'id')
    date_hierarchy = 'created_at'
    inlines = [OrderItemInline]  # Display related order items within the order form

    def get_expected_delivery(self, obj):
        return obj.expected_delivery if obj.expected_delivery else 'Not Set'
    get_expected_delivery.short_description = 'Expected Delivery'

    # You can override other methods here if you want custom actions or views for the admin panel

# Register the models to be accessible in the admin interface
admin.site.register(Order, OrderAdmin)
admin.site.register(OrderItem)
