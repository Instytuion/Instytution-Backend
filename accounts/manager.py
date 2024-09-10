
from django.contrib.auth.models import  BaseUserManager
class CustomUserManager(BaseUserManager):
    def create_user(self, email, password, register_mode, **extra_fields):
        print(extra_fields)
        if not email:
            raise ValueError(_('The Email field must be set'))

        email = self.normalize_email(email)
        user = self.model(email=email, register_mode=register_mode, **extra_fields)

        if password:  
            user.set_password(password)
        else:  
            raise ValueError(_('The Email field must be set'))

        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, register_mode='email',  **extra_fields):
        user = self.create_user(email, register_mode=register_mode, password=password,)
        user.is_superuser = True  
        user.is_staff = True 
        user.register_mode = 'email' 
        user.role='admin'
        user.save(using=self._db)
        return user
