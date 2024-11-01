from django.shortcuts import render
from rest_framework.views import APIView
from .serializers import *
from django.db import transaction 
from django.shortcuts import get_object_or_404
from payments.razorpay.main import RazorpayClient
from rest_framework.response import Response
from rest_framework import status

rz_client = RazorpayClient()

class CreateOrderView(APIView):
    '''
    To create an order
    '''
    def post(self, request):
        print('request data is :',request.data)
        serializer = OrderSerializer(data = request.data)
        serializer.is_valid (raise_exception=True)

        # order_data = serializer.validated_data
        # print('order data:', order_data)

        # item_data = order_data.pop('item_id', None)

        with transaction.atomic():

            order = Order.objects.create(
                user = request.user,
                total_amount = serializer.validated_data['total_amount'],
                delivery_charge = serializer.validated_data['delivery_charge'],
            )

        product_to_update = []

        for item in serializer.validated_data['items']:
            product = get_object_or_404(ProductDetails.objects.select_for_update(),id=item['product'])
            quantity = item['quantity']
            
            OrderItem.objects.create(
                order = order,
                product = product,
                quantity = quantity,
                total_price = quantity * product.price
            )
            product.stock -= quantity
            product_to_update.append(product)
        
        ProductDetails.objects.bulk_update(product_to_update, ['stock'])
        
        try:
            razorpay_order = rz_client.create_order(order.total_amount,"INR")
            print('oder id and detrails fropm razorpay is :',razorpay_order)
            ProductPayment.objects.create(
                order=order,
                payment_order_id=razorpay_order['id'],
                amount=order.total_amount,
                payment_method='Razorpay',
            )
            return Response({
            "order_id": order.id,
            "razorpay_order_id": razorpay_order['id'],
            "total_amount": str(order.total_amount),
            "status": order.status,
            "expected_delivery": order.expected_delivery.isoformat() if order.expected_delivery else None,
            }, status=status.HTTP_201_CREATED)
        except Exception as e:
            print('Error while creating razorpay order - ', str(e))
            return Response({"message":str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)