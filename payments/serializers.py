from rest_framework import serializers
from .models import CoursePayment

class CreateRazorpayOrderSerializer(serializers.Serializer):
    amount = serializers.IntegerField()
    currency = serializers.CharField()
    batch_id = serializers.IntegerField()

class CoursePaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = CoursePayment
        fields = ['batch', 'payment_id', 'order_id', 'signature', 'amount']

    def create(self, validated_data):
        validated_data['amount'] = validated_data['amount'] / 100 #To correct amount recieved from RZpay
        user = self.context['user']
        return CoursePayment.objects.create(user=user, **validated_data)