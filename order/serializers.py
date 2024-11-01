from  rest_framework import serializers
from .models import *
from payments.models import ProductPayment
from accounts.models import ProductDetails

class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = ['id', 'product', 'quantity', 'total_price', 'sub_order_id']
        # fields = '__all__'

class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True)
    
    class Meta:
        model = Order
        fields = ['id', 'status', 'total_amount', 'expected_delivery', 'delivery_charge', 'created_at', 'items']
        # fields = '__all__'
    def validate(self, data):
        print('data froom validated os :L',data)
        """
        Validates the order items and calculates the total amount.
        """
        items = data.get('items', [])
        print('items ',items.product.id)
        total_amount = 0

        for item in items:
            print('item is :',item)
            product_id = item.get('product_id')
            print('product_id ::::', product_id)
            quantity = item.get('quantity')
            try:
                product = ProductDetails.objects.select_for_update().get(id=item['product'])
            except ProductDetails.DoesNotExist:
                raise serializers.ValidationError(f"Product with ID {item['product']} does not exist.")

            if product.stock <  quantity:
                raise serializers.ValidationError(f"Not enough stock for {product.name}.")
                            
            total_amount += product.price * quantity

        if total_amount < 1000:
            """ 
            Delivery Charge
            """
            data['delivery_charge'] = 50
        else:
            data['delivery_charge'] = 0
        
        data['total_amount'] = total_amount + data['delivery_charge']
        print('Last Data from the serializer is :',data)
        return data



class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductPayment
        # fields = ['order', 'payment_order_id', 'payment_status', 'amount', 'payment_method', 'created_at']
        fields = '__all__'