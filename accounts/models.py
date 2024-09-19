from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.db import models
from django.utils.translation import gettext_lazy as _
from .manager import CustomUserManager
from cloudinary.models import CloudinaryField
from rest_framework_simplejwt.tokens import RefreshToken




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
