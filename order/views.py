from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import OrderSerializer, PaymentVerificationSerializer
from .models import Order, ProductDetails,OrderItem
from payments.models import ProductPayment
from django.db import transaction
from django.utils import timezone
from datetime import timedelta
from decimal import Decimal
from payments.razorpay.main import RazorpayClient
from django.conf import settings
from rest_framework.serializers import ValidationError
from rest_framework import serializers 
from accounts.models import Cart

rz_client = RazorpayClient()

class CreateOrderView(APIView):
    '''
    To create an order
    '''
    def post(self, request):
        print('request data is :', request.data)
        serializer = OrderSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        total_amount = serializer.validated_data['total_amount']
        print('total amount',total_amount)
        try:
            razorpay_order = rz_client.create_order(amount=total_amount, currency="INR")

            return Response(
                {
                "razorpay_order_id": razorpay_order['id'],
                    "total_amount": total_amount,
                },
                status=status.HTTP_201_CREATED
            )
        except Exception as e:
            print('Error while creating razorpay order - ', str(e))
            return Response({"message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
from django.db.models import F

class VerifyOrderView(APIView):
    def post(self, request):
        serializer = PaymentVerificationSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        data = serializer.validated_data
        razorpay_order_id = data.get("razorpay_order_id")
        razorpay_payment_id = data.get("razorpay_payment_id")
        razorpay_signature = data.get("razorpay_signature")
        total_amount = Decimal(data.get("total_amount", 0))
        delivery_charge = Decimal(data.get("delivery_charge", 0))
        address_id = data.get("address_id")
        
        try:
            rz_client.verify_payment(razorpay_order_id, razorpay_payment_id, razorpay_signature)
        except ValidationError as e:
            return Response({"message": f"Payment verification failed: {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)

        with transaction.atomic():
            order = Order.objects.create(
                user=request.user,
                status="confirmed",
                total_amount=total_amount,
                delivery_charge=delivery_charge,
                expected_delivery=timezone.now() + timedelta(days=5),
                address_id=address_id,
            )

            order_items = []
            for item_data in data.get("items", []):
                product_id = item_data['product']
                quantity = item_data['quantity']
                total_price = item_data['total_price']

                product = ProductDetails.objects.select_for_update().get(id=product_id)
                if product.stock < quantity:
                    raise serializers.ValidationError(f"Insufficient stock for {product.name}")

                order_items.append(OrderItem(
                    order=order,
                    product=product,
                    quantity=quantity,
                    total_price=total_price
                ))

                # Update the product stock with F() expression
                ProductDetails.objects.filter(id=product_id).update(stock=F('stock') - quantity)

            OrderItem.objects.bulk_create(order_items)

            ProductPayment.objects.create(
                order=order,
                payment_order_id=razorpay_order_id,
                payment_status="successful",
                amount=total_amount,
                payment_method="razorpay",
            )

            Cart.objects.filter(user=request.user).delete()

        return Response({"message": "Order created and payment verified successfully"}, status=status.HTTP_201_CREATED)

        return Response({"message": "Order created and payment verified successfully"}, status=status.HTTP_201_CREATED)
    # def post(self, request):
    #     serializer = PaymentVerificationSerializer(data=request.data)
    #     if serializer.is_valid():
    #         try:
    #             razorpay_payment_id = request.data.get("razorpay_payment_id")
    #             razorpay_order_id = request.data.get("razorpay_order_id")
    #             razorpay_signature = request.data.get("razorpay_signature")
    #             total_amount = Decimal(request.data.get("total_amount", 0))
    #             delivery_charge = Decimal(request.data.get("delivery_charge", 0))

                
    #             with transaction.atomic():
    #                 try:
    #                     rz_client.verify_payment(
    #                         razorpay_order_id,
    #                         razorpay_payment_id,
    #                         razorpay_signature
    #                     )
    #                 except ValidationError as e:
    #                     return Response({
    #                         "status_code": status.HTTP_400_BAD_REQUEST,
    #                         "message": f'Payment verification failed. Error is - {str(e)}'
    #                     }, status=status.HTTP_400_BAD_REQUEST)


    #                 order = Order.objects.create(
    #                     user=request.user,
    #                     status="confirmed",
    #                     total_amount=total_amount,
    #                     delivery_charge=delivery_charge,
    #                     expected_delivery=timezone.now() + timedelta(days=5),
    #                     address_id=request.data.get('address_id')
    #                 )

    #                 for item in request.data.get('items', []):
    #                     product = ProductDetails.objects.select_for_update().get(id=item['product'])
    #                     if product.stock < item['quantity']:
    #                         raise serializers.ValidationError(f"Insufficient stock for {product.name}")
    #                     OrderItem.objects.create(
    #                         order=order,
    #                         product=product,
    #                         quantity=item['quantity'],
    #                         total_price=item['total_price'],
    #                     )
    #                     product.stock -= item['quantity']
    #                     product.save()

    #                 ProductPayment.objects.create(
    #                     order=order,
    #                     payment_order_id=razorpay_order_id,
    #                     payment_status="successful",
    #                     amount=total_amount,
    #                     payment_method="razorpay",
    #                 )

    #             return Response({"message": "Order created and payment verified successfully"}, status=status.HTTP_201_CREATED)
            
    #         except Exception as e:
    #             return Response({"message": f"Error during payment verification: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    #     return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

