
from django.contrib.auth.models import  BaseUserManager
class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError(_('The Email field must be set'))

        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)

        if password:  # Set password if provided (normal users)
            user.set_password(password)
        else:  # Set password to null for Google OAuth users
            user.password = None

        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        user = self.create_user(email, role='admin', password=password)
        user.is_superuser = True  
        user.is_staff = True  
        user.save(using=self._db)
        return user
