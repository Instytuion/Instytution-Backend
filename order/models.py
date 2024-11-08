from django.db import models
from accounts.models import *
from django.utils import timezone
import uuid
from decimal import Decimal
from datetime import timedelta

class Order(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('awaiting_payment', 'Awaiting Payment'),
        ('confirmed', 'Confirmed'),
        ('shipped', 'Shipped'),  
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
    ]
    
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    address = models.ForeignKey(UserAddresses, on_delete=models.CASCADE) 
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    expected_delivery = models.DateTimeField(blank=True, null=True)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    delivery_charge = models.DecimalField(max_digits=6, decimal_places=2, default=0.00)  
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def calculate_total(self):
        """Calculates and updates the total amount for the order, including delivery charge."""
        items_total = sum(item.total_price for item in self.items.all())
        self.total_amount = items_total + Decimal(self.delivery_charge)
        self.save()

    def  set_expected_delivery(self):
        """Sets the expected delivery date for the order."""
        if self.status == 'confirmed':
            self.expected_delivery = timezone.now() + timedelta(days=5) 
            self.save()

    def save(self, *args, **kwargs):
        if not self.total_amount:
            self.calculate_total()
        
        if not self.expected_delivery and self.status == 'confirmed':
            self.set_expected_delivery()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Order {self.id} by {self.user.email}"


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(ProductDetails, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    sub_order_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)

    def __str__(self):
        return f"{self.quantity} x {self.product.product.name} in {self.order}"