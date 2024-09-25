from rest_framework.views import APIView
from rest_framework import status
from rest_framework.serializers import ValidationError
from rest_framework.response import Response
from .serializers import CreateRazorpayOrderSerializer, CoursePaymentSerializer
from payments.razorpay.main import RazorpayClient
from courses.models import BatchStudents, Batch
from accounts.models import CustomUser
from django.db import transaction

rz_client = RazorpayClient()

class CreateRazorpayOrderView(APIView):
    def post(self, request):
        razorpay_create_order_serializer = CreateRazorpayOrderSerializer(
            data = request.data
        )
        if razorpay_create_order_serializer.is_valid():
            amount = razorpay_create_order_serializer.validated_data.get("amount")
            currency = razorpay_create_order_serializer.validated_data.get("currency")
            rz_order_response = rz_client.create_order(amount=amount, currency=currency)
            response = {
                "status_code": status.HTTP_201_CREATED,
                "message": "Razorpay order created",
                "data": rz_order_response
            }
            return Response(response, status=status.HTTP_201_CREATED)
        else:
            response = {
                "status_code": status.HTTP_400_BAD_REQUEST,
                "message": "Bad request",
                "error": razorpay_create_order_serializer.errors
            }
            return Response(response, status=status.HTTP_400_BAD_REQUEST)
        
class CreteCoursePaymentView(APIView):
    def post(self, request):
        payment_serializer = CoursePaymentSerializer(
            data = request.data,
            context={'user': request.user} 
        )
        if payment_serializer.is_valid():
            razorpay_order_id = payment_serializer.validated_data.get('order_id')
            razorpay_payment_id = payment_serializer.validated_data.get('payment_id')
            razorpay_signature = payment_serializer.validated_data.get('signature')
            with transaction.atomic():
                try:
                    rz_client.verify_payment(
                        razorpay_order_id,
                        razorpay_payment_id,
                        razorpay_signature
                    )
                except ValidationError as e:
                    return Response({
                        "status_code": status.HTTP_400_BAD_REQUEST,
                        "message": f'Payment verification failed. Error is - {str(e)}'
                    }, status=status.HTTP_400_BAD_REQUEST)

                course_payment = payment_serializer.save()
                user = request.user
                batch = payment_serializer.validated_data.get('batch')
                # batch = Batch.objects.get(id=batch_data.id)
                BatchStudents.objects.create(batch=batch, student=user)
                response = {
                    "status_code": status.HTTP_201_CREATED,
                    "message": "Course payment and BatchStudent created successfully.",
                }
                return Response(response, status=status.HTTP_201_CREATED)
        else:
            response = {
                "status_code": status.HTTP_400_BAD_REQUEST,
                "message": "Bad request. Serializer validation failed.",
                "error": payment_serializer.errors
            }
            return Response(response, status=status.HTTP_400_BAD_REQUEST)