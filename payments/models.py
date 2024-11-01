from django.db import models
from accounts.models import CustomUser
from courses.models import Batch
from order.models import Order
class CoursePayment(models.Model):
    batch = models.ForeignKey(
        Batch, 
        related_name='batch_payments', 
        on_delete=models.SET_NULL,
        null=True
    )
    user = models.ForeignKey(
        CustomUser, 
        related_name='user_payments', 
        on_delete=models.SET_NULL,
        null=True
    )
    payment_id = models.CharField(max_length=100)
    order_id = models.CharField(max_length=100)
    signature = models.CharField(max_length=250)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.id)


class ProductPayment(models.Model):
    STATUS_CHOICES = [
        ('initiated', 'Initiated'),
        ('successful', 'Successful'),
        ('failed', 'Failed'),
    ]

    order = models.OneToOneField(Order, on_delete=models.CASCADE, related_name="payment")
    payment_order_id = models.CharField(max_length=100, unique=True)
    payment_status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='initiated')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_method = models.CharField(max_length=50)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Payment {self.payment_order_id} for Order {self.order.id}"