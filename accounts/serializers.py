from rest_framework import serializers
from .models import CustomUser
from django.core.cache import cache
  

class UserSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(required=True)
    password = serializers.CharField(write_only=True, min_length=4, required=True)

    class Meta:
        model = CustomUser
        fields = '__all__'

    def validate_email(self, value):
        """Check if the email is already in use."""
        if CustomUser.objects.filter(email=value).exists():
            raise serializers.ValidationError("A user with this email already exists.")
        return value

class OTPSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    otp = serializers.CharField(required=True, min_length=6, max_length=6)
    password = serializers.CharField(required=True)

    def validate(self, data):
        """Validate that the OTP matches the one stored in the cache."""
        email = data.get('email')
        otp = data.get('otp')
        
        cached_otp = cache.get(f"otp_{email}")
        print('cached_otp:',cached_otp)
        if cached_otp is None:
            cache.delete(f"otp_{email}")
            raise serializers.ValidationError({"otp": "OTP has expired."})
        if cached_otp != otp:
            raise serializers.ValidationError({"otp": "Invalid OTP."})
        
        return data
    
class SignInSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    password = serializers.CharField(required=True)

    