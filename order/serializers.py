from  rest_framework import serializers
from .models import *
from payments.models import ProductPayment
from accounts.models import ProductDetails
import hmac
import hashlib
from django.conf import settings
from rest_framework import serializers
from payments.razorpay.main import RazorpayClient
rz_client = RazorpayClient()

class OrderItemSerializer(serializers.Serializer):
    product = serializers.IntegerField()  # Expect product ID as integer
    quantity = serializers.IntegerField()
    total_price = serializers.DecimalField(max_digits=10, decimal_places=2)

    # def validate(self, data):
    #     product_id = data.get('product')  # Extracting product ID as integer
    #     try:
    #         # Fetching product instance based on product ID to check validity
    #         product = ProductDetails.objects.get(id=product_id)
    #         # Additional validation logic (if needed)
    #     except ProductDetails.DoesNotExist:
    #         raise serializers.ValidationError("Invalid product ID.")

    #     return data
    def validate(self, data):
        product_id = data.get('product')  # Extracting product ID as integer
        try:
            # Fetching product instance based on product ID to check validity
            product = ProductDetails.objects.get(id=product_id)
            quantity = data.get('quantity')
            # Calculate the total price for the item
            data['total_price'] = product.price * quantity
        except ProductDetails.DoesNotExist:
            raise serializers.ValidationError("Invalid product ID.")

        return data

class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True)
    
    class Meta:
        model = Order
        fields = ['id', 'status', 'total_amount', 'expected_delivery', 'delivery_charge', 'created_at', 'items']
    
    def validate(self, data):
        print('Data from validated method:', data)

        # Initialize total amount and delivery charge
        items = data.get('items', [])
        
        total_amount = 0

        for item in items:
            product_id = item.get('product')
            quantity = item.get('quantity')
            print('product id anad qunaity', product_id, quantity)

            try:
                product = ProductDetails.objects.get(id=product_id)
            except ProductDetails.DoesNotExist:
                raise serializers.ValidationError(f"Product with ID {product_id} does not exist.")

            if product.stock < quantity:
                print('product stock',  product.stock)
                raise serializers.ValidationError(f"Not enough stock for {product.product   .name}.")


            # print('toatl amount and product pric dand product quantity', total_amount, product.price, quantity)
        print('delivery charge', data.get('delivery charge'))
        data['delivery_charge'] = 0 if total_amount >= 1000 else 40
        print('delivery charge', data.get('delivery charge'))
        
        data['total_amount'] = float(data['total_amount']) + data['delivery_charge']
        # print('total amount', data(['total amount']))

        print('Final validated data:', data)
        return data


class PaymentVerificationSerializer(serializers.Serializer):
    razorpay_payment_id = serializers.CharField()
    razorpay_order_id = serializers.CharField()
    razorpay_signature = serializers.CharField()
    total_amount = serializers.DecimalField(max_digits=10, decimal_places=2)
    delivery_charge = serializers.DecimalField(max_digits=5, decimal_places=2)
    address_id = serializers.IntegerField()
    items = OrderItemSerializer(many=True)

    def validate(self, data):
        """
        Custom validation logic for payment verification.
        Here we can verify if the signature matches, if the amount is correct, etc.
        """
        
        total_amount = data.get('total_amount') 
        print('totaotoatoatoaotoaot',total_amount)
        delivery_charge = 40 if total_amount < 1000 else 0
        items = data.get('items')
        print('items:', items)

        # Calculate the expected total amount
        expected_total = sum(item['quantity'] * item['total_price'] for item in items) + delivery_charge
        print('toal amount , expected total', expected_total, total_amount)
        if total_amount != expected_total:
            raise serializers.ValidationError("Total amount does not match the calculated amount.")

        # Validate the Razorpay payment signature
        razorpay_order_id = data.get("razorpay_order_id")
        razorpay_payment_id = data.get("razorpay_payment_id")
        razorpay_signature = data.get("razorpay_signature")
        # generated_signature = hmac.new(
        #     key=bytes(settings.RAZORPAY_KEY_ID, 'utf-8'),
        #     msg=f"{razorpay_order_id}|{razorpay_payment_id}".encode('utf-8'),
        #     digestmod=hashlib.sha256
        # ).hexdigest()
           
        

        return data