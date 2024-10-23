from rest_framework import serializers
from .models import CustomUser
from django.core.cache import cache
from .utils import Google_signin, register_google_user
from rest_framework.exceptions import AuthenticationFailed
from accounts import constants
from django.conf import settings


class UserSerializer(serializers.ModelSerializer):
    email         = serializers.EmailField(required=True)
    password      = serializers.CharField(write_only=True, min_length=4, required=False)
    register_mode = serializers.CharField(required=False)
    profile_picture = serializers.ImageField(use_url=True, required=False)

    class Meta:
        model    = CustomUser
        fields   = ['id', 'email', 'password', 'role', 'first_name', 'last_name', 'profile_picture', 'is_active', 'register_mode']

    def validate_email(self, value):
        """Check if the email is already in use."""
        if CustomUser.objects.filter(email=value).exists():
            raise serializers.ValidationError("A user with this email already exists.")
        return value
    
    # def validate(self, data):
    #     """
    #     Ensure password is provided only for creation (POST), not for updates (PATCH/PUT).
    #     """
    #     if not self.instance and not data.get('password'):
    #         raise serializers.ValidationError({"password": "Password is required for new users."})
    #     return data
        
    def update(self, instance, validated_data):
        """
        Update user instance with validated data. Do not handle password updates.
        """

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()
        return instance 

class OTPSerializer(serializers.Serializer):
    email    = serializers.EmailField(required=True)
    otp      = serializers.CharField(required=True, min_length=6, max_length=6)
    password = serializers.CharField(required=True)

    def validate(self, data):
        email = data.get('email')
        otp = data.get('otp')

        # Validate that the OTP matches the one stored in the cache.
        cached_otp = cache.get(f"otp_{email}")
        print('cached_otp:', cached_otp)
        if cached_otp is None:
            raise serializers.ValidationError({"otp": "OTP has expired."})
        if cached_otp != otp:
            raise serializers.ValidationError({"otp": "Invalid OTP."})

        return data
    

    
class SignInSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    password = serializers.CharField(required=True)

    def validate_email(self, value):
        """
        Validates the email to check if the user is registered via Google. 
        If so, prompts the user to log in with Google.
        """
        user = CustomUser.objects.filter(email=value).first()
    
        if user and user.register_mode == 'google':
            raise serializers.ValidationError("This email is registered via Google. Please Sign in with Google.")
        
        return value
            





class GoogleSignInSerializer(serializers.Serializer):
    """
    Serializer for Google sign-in.
    """
    access_token=serializers.CharField()

    def validate_access_token(self, access_token):
        """
        Validate the access token and register the user if valid.
        """
        user_data=Google_signin.validate(access_token)
        try:
            user_data['sub']  
        except:
            raise serializers.ValidationError(
                constants.ERROR_TOKEN_EXPIRED_OR_INVALID
            )
        
        if user_data['aud'] != settings.GOOGLE_CLIENT_ID:
                raise AuthenticationFailed(constants.ERROR_VERIFY_USER)

        email=user_data['email']
        user, tokens = register_google_user(email)
        user_serializer = UserSerializer(user)
        return {
            "access": tokens['access'],
            "refresh": tokens['refresh'],
            "user": user_serializer.data,
            "message": constants.USER_LOGGED_IN_SUCCESSFULLY,
        }



class VerifyEmailUpdateOTpSerializer(serializers.Serializer):
    """
    Serializer for updating profile with email of a CustomUser.
    """
    email      = serializers.EmailField(required=True)
    otp        = serializers.CharField(required=True, min_length=6, max_length=6)
    first_name = serializers.CharField(required=False)
    last_name  = serializers.CharField(required=False)

    def validate(self, data):
        email = data.get('email')
        otp = data.get('otp')

        # Validate that the OTP matches the one stored in the cache.
        cached_otp = cache.get(f"otp_{email}")
        print('cached_otp:', cached_otp)
        if cached_otp is None:
            raise serializers.ValidationError({"otp": "OTP has expired."})
        if cached_otp != otp:
            raise serializers.ValidationError({"otp": "Invalid OTP."})

        return data

        
class PasswordResetRequestSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate_email(self, value):
        if not CustomUser.objects.filter(email=value).exists():
            raise serializers.ValidationError("No user registered with this email address.")
        return value
    
class PasswordResetConfirmSerializer(serializers.Serializer):
    password = serializers.CharField(write_only=True, required=True)

from .models import Whishlists
from store.serializers import ProductImagesSerializer
from store.models import ProductDetails
class ProductSpecificDetailSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.name')
    product_description = serializers.CharField(source='product.description') 
    product_id = serializers.IntegerField(source='product.id')
    product_images = ProductImagesSerializer(source='product.images', many=True)  
    class Meta:
        model = ProductDetails
        fields = ['product_name', 'product_description', 'product_id', 'product_images','size','color','price','stock']
class WishlistItemSerializer(serializers.ModelSerializer):
    product = ProductSpecificDetailSerializer()
    class Meta:
        model = Whishlists
        fields = ['id', 'product', 'added_at']