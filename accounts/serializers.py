from rest_framework import serializers
from .models import *
from django.core.cache import cache
from .utils import Google_signin, register_google_user
from rest_framework.exceptions import AuthenticationFailed
from accounts import constants
from django.conf import settings
from store.serializers import ProductImagesSerializer
from store.models import ProductDetails
from django.db import IntegrityError

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

class ProductSpecificDetailSerializer(serializers.ModelSerializer):
    average_rating = serializers.ReadOnlyField(source='product.average_rating')
    rating_count   = serializers.ReadOnlyField(source='product.rating_count')
    product_name = serializers.CharField(source='product.name', read_only=True)
    product_description = serializers.CharField(source='product.description', read_only=True) 
    product_id = serializers.IntegerField(source='product.id', read_only=True)
    product_images = ProductImagesSerializer(source='product.images', many=True, read_only=True)  
    
    class Meta:
        model = ProductDetails
        fields = [
            'product_name',
            'product_description',
            'product_id',
            'product_images',
            'id',
            'size',
            'color',
            'price',
            'stock',
            'average_rating',
            'rating_count',
            
        ]
        
    def create(self, validated_data):
        request = self.context.get('request')
        product_id = request.parser_context['kwargs'].get('pk') 
        
        try:
            product = Products.objects.get(id=product_id)
        except Products.DoesNotExist:
            raise serializers.ValidationError({
                "product_id": "Invalid product ID. Product does not exist."
            })
        
        validated_data['created_by'] = request.user
        validated_data['updated_by'] = request.user

        try:
            product_details = ProductDetails.objects.create(product=product, **validated_data)
        except IntegrityError:
            raise serializers.ValidationError({
                "detail": "This product detail already exists with the specified size and color."
            })
        
        return product_details
    
    def update(self, instance, validated_data):
        print('entered in update method')
        request = self.context.get('request')
        print('request.data', request.data)
        
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.updated_by = request.user
        
        try:
            instance.save()
        except IntegrityError:
            raise serializers.ValidationError({
                "detail": "This product detail already exists with the specified size and color."
            })
    
        return instance


        

class WishlistItemSerializer(serializers.ModelSerializer):
    product = ProductSpecificDetailSerializer(read_only=True)
    class Meta:
        model = Whishlists
        fields = ['id', 'product', 'added_at']


class CartItemSerializer(serializers.ModelSerializer):
    total_price = serializers.SerializerMethodField() 
    product = ProductSpecificDetailSerializer(read_only=True)

    class Meta:
        model = CartItem
        fields = ['id', 'product', 'quantity', 'total_price']

    def get_total_price(self, obj):
        return obj.quantity * obj.product.price
    
    def create(self, validated_data):
        request = self.context.get('request')
        product_id = request.parser_context['kwargs'].get('pk')  
        user = request.user
        cart, created = Cart.objects.get_or_create(user=user)
        product = ProductDetails.objects.get(id=product_id)
        quantity = validated_data.get('quantity')

        existing_cart_item = CartItem.objects.filter(cart=cart, product=product).first()
        if existing_cart_item:
            total_quantity = quantity 
        else:
            total_quantity = quantity

        if total_quantity > 12:
                raise serializers.ValidationError("We're Sorry, Only 12 Units Allowed.")
        
        if existing_cart_item:
            existing_cart_item.quantity = total_quantity
            existing_cart_item.save()
            return existing_cart_item
        else:
            cart_item = CartItem.objects.create(cart=cart, product=product, quantity=quantity)
            return cart_item
        

class AddressSerializer(serializers.ModelSerializer):
    user = serializers.ReadOnlyField(source='user.email')  # Assuming user has an email field

    class Meta:
        model = UserAddresses
        fields = [
            'id',
            'user',
            'name',
            'house_name',
            'street_name_1',
            'street_name_2',
            'city',
            'state',
            'pincode',
            'phone_number',
            'is_active'
        ]
    def validate(self, data):
        """
        Custom validation for checking if an address with the same pincode and phone number already exists.
        """
        user = self.context['request'].user  
        print('user is %s' % user)
        pincode = data.get('pincode')
        phone_number = data.get('phone_number')

        if UserAddresses.objects.filter(user=user).count() >= 3:
            raise serializers.ValidationError("You can only have up to 3 addresses.")

        instance = self.instance
        if instance:
            existing_addresses = UserAddresses.objects.filter(
                pincode=pincode,
                phone_number=phone_number,
                user=user
            ).exclude(pk=instance.pk)  
        else:
            existing_addresses = UserAddresses.objects.filter(
                pincode=pincode,
                phone_number=phone_number,
                user=user
            )

        if existing_addresses.exists():
            raise serializers.ValidationError("An address with this pincode and phone number already exists for this customer.")

        return data

    def create(self, validated_data):
        """
        Handle the creation of a new Address instance.
        """
        return super().create(validated_data)

    def update(self, instance, validated_data):
        """
        Handle the update of an existing Address instance.
        Only fields in validated_data are updated.
        """
        for field, value in validated_data.items():
            setattr(instance, field, value)
        instance.save()
        return instance