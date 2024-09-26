from rest_framework.views import APIView
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.serializers import ValidationError
from rest_framework.response import Response
from .serializers import CreateRazorpayOrderSerializer, CoursePaymentSerializer
from payments.razorpay.main import RazorpayClient
from courses.models import BatchStudents, Batch
from django.db import transaction

rz_client = RazorpayClient()

class CreateRazorpayOrderView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request):
        """
        This view first checks if the user already enrolled for a batch for the requested date.
        if yes it rerurns a message, if no it returns a razorpay created order.
        """
        razorpay_create_order_serializer = CreateRazorpayOrderSerializer(
            data = request.data
        )
        if razorpay_create_order_serializer.is_valid():
            amount = razorpay_create_order_serializer.validated_data.get("amount")
            currency = razorpay_create_order_serializer.validated_data.get("currency")
            batch_id = razorpay_create_order_serializer.validated_data.get("batch_id")
            enrolled_already = False
            batch_name= ''
            user = request.user
            requested_batch = Batch.objects.get(id=batch_id)
            requested_start_date = requested_batch.start_date
            users_batch_students_instance = BatchStudents.objects.filter(student=user)
            users_batch_date_list = [
                (batch.batch.start_date, batch.batch.end_date, batch.batch.name) for batch in users_batch_students_instance
                ]
            for item in users_batch_date_list:
                if item[0] <= requested_start_date <= item[1]:
                    enrolled_already = True
                    batch_name = item[2]
                    break
            if enrolled_already:

                data = {
                    "message": f"User already enrolled for \"{batch_name}\" batch during selected dates.",
                    "enrolled_already": enrolled_already,
                    "batch_name": batch_name
                }
                response = {"data": data}
                return Response(response, status=status.HTTP_200_OK)

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
    permission_classes = [IsAuthenticated]
    def post(self, request):
        """
        This view first verifys razorpay payment in the request and if valid then it 
        creates payment and batch student instance in atomic.
        """
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