from django.urls import path
from .views import (
    UserSignUpView,
    UserOTPVerifyView,
    SignInUserView,
    ResentOTPView,
    SubAdminCreateView,
    GoogleOauthSignInview
)

urlpatterns = [
    path('sign-up/', UserSignUpView.as_view(), name='user_sign_up'),
    path('verify-otp/', UserOTPVerifyView.as_view(), name='verify_otp'),
    path('sign-in/', SignInUserView.as_view(), name='sign_in'),
    path('resent-otp/', ResentOTPView.as_view(), name='resent_otp'),
    path('subadmin-create/', SubAdminCreateView.as_view(), name='subAdmin_create'),
    path('google-auth/', GoogleOauthSignInview.as_view(), name='subAdmin_create'),
]
