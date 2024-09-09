from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.db import models
from django.utils.translation import gettext_lazy as _
from .manager import CustomUserManager
from cloudinary.models import CloudinaryField


ROLE_CHOICES = (
    ('admin', 'Admin'),
    ('user', 'User'),
    ('instructor', 'Instructor'),
    ('course_admin', 'Course Admin'),
    ('shop_admin', 'Shop Admin')
)

class CustomUser(AbstractBaseUser, PermissionsMixin):
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
    
    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    def __str__(self):
        return self.email
