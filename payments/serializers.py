from rest_framework import serializers
from .models import CoursePayment

class CreateRazorpayOrderSerializer(serializers.Serializer):
    amount = serializers.IntegerField()
    currency = serializers.CharField()

class CoursePaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = CoursePayment
        fields = ['batch', 'payment_id', 'order_id', 'signature', 'amount']

    def create(self, validated_data):
        user = self.context['request'].user
        CoursePayment.objects.create(user=user, **validated_data)