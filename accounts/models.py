from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.db import models
from django.utils.translation import gettext_lazy as _
from .manager import CustomUserManager
from cloudinary.models import CloudinaryField
from rest_framework_simplejwt.tokens import RefreshToken
from store.models import ProductDetails,Products
from django.core.validators import MinValueValidator, MaxValueValidator 
from django.core.exceptions import ValidationError


class CustomUser(AbstractBaseUser, PermissionsMixin):

    ROLE_CHOICES = (
        ('admin', 'Admin'),
        ('user', 'User'),
        ('instructor', 'Instructor'),
        ('course_admin', 'Course Admin'),
        ('shop_admin', 'Shop Admin')
    )
    email = models.EmailField(_('email address'), unique=True)
    first_name = models.CharField(max_length=30, blank=True, null=True)
    last_name = models.CharField(max_length=30, blank=True, null=True)
    profile_picture = CloudinaryField('image', blank=True, null=True)
    is_active = models.BooleanField(default=True)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='user')
    is_staff = models.BooleanField(default=False)
    is_superuser= models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    register_mode=models.CharField(null=False)
    
    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    
    
    
    @property
    def tokens(self) -> dict[str,str]:
        print('reached in gen tokens')
        
        referesh = RefreshToken.for_user(self)
        
        return{
           'refresh': str(referesh),
            'access': str(referesh.access_token),
        } 

    @classmethod
    def get_valid_roles(cls):
        return [choice[0] for choice in cls.ROLE_CHOICES]

    def __str__(self):
        return self.email



class Whishlists(models.Model):
    user = models.ForeignKey(CustomUser,related_name='wishlist', on_delete=models.CASCADE)
    product = models.ForeignKey(ProductDetails, related_name='wishlist_items', on_delete=models.CASCADE)
    added_at = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return f"{self.user.email} - {self.product.product.name}"
    
class Cart(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name="cart", null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Cart of {self.user}"

    def get_total_price(self):
        total = sum(item.get_total_price() for item in self.items.all())
        return total

    def get_total_items(self):
        return sum(item.quantity for item in self.items.all())
    
class CartItem(models.Model):
    cart = models.ForeignKey(Cart, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(ProductDetails, on_delete=models.CASCADE) 
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.quantity} x {self.product.product.name}"

    def get_total_price(self):
        return self.quantity * self.product.price




class Rating(models.Model):
    product = models.ForeignKey(Products, related_name='ratings', on_delete=models.CASCADE)
    user  = models.ForeignKey(CustomUser, related_name='ratings', on_delete=models.CASCADE)
    rating = models.PositiveSmallIntegerField(
        validators=[
            MinValueValidator(1),
            MaxValueValidator(5)
        ]
    )
    feedback = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('product', 'user')

    def __str__(self):
        return f"{self.user.email} rated {self.product.name} - {self.rating}"

class RatingImage(models.Model):
    rating = models.ForeignKey(Rating, related_name='rating_images', on_delete=models.CASCADE)
    image = CloudinaryField('image', blank=True, null=True, folder='ratings/')
    
    def __str__(self):
        return f"Image for rating {self.rating.id}"


class UserAddresses(models.Model):
    '''
    Address of each customer and guest will be saves here. name and phone_number 
    will be a unique combination for each customer.
    '''
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    name = models.CharField(max_length=100, blank=False, null=False)
    house_name = models.CharField(max_length=100, blank=False, null=False)
    street_name_1 = models.CharField(max_length=100, blank=False, null=False)
    street_name_2 = models.CharField(max_length=100, blank=True, null=True)
    city = models.CharField(max_length=100, blank=False, null=False)
    state = models.CharField(max_length=100, blank=False, null=False)
    pincode = models.CharField(max_length=10, blank=False, null=False)
    phone_number = models.CharField(max_length=13)
    is_active = models.BooleanField(default=True)

    class Meta:
        # unique_together = ('user', 'pincode', 'phone_number')
        
        indexes = [
            models.Index(fields=['user', 'pincode', 'phone_number']),
        ]

    def __str__(self):
        return f"{self.user}, {self.name}, {self.house_name}"   
