from django.urls import path
from .views import UserSignUpView,UserOTPVerifyView,SignInUserView

urlpatterns = [
    path('sign-up/', UserSignUpView.as_view(), name='user_sign_up'),
    path('verify-otp/', UserOTPVerifyView.as_view(), name='verify_otp'),
    path('sign-in/', SignInUserView.as_view(), name='sign_in'),
]
