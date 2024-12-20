from django.urls import path
from .views import *
from rest_framework_simplejwt.views import TokenRefreshView


urlpatterns = [
    path('sign-up/', UserSignUpView.as_view(), name='user_sign_up'),
    path('verify-otp/', UserOTPVerifyView.as_view(), name='verify_otp'),
    path('sign-in/', SignInUserView.as_view(), name='sign_in'),
    path('resent-otp/', ResentOTPView.as_view(), name='resent_otp'),
    path('subadmin-create/', SubAdminCreateView.as_view(), name='subAdmin_create'),
    path('instructor-create/', InstructorCreateView.as_view(), name='instructor_create'),
    path('google-auth/', GoogleOauthSignInview.as_view(), name='google_auth'),
    path('user-profile/', UserProfileRetrieveUpdateView.as_view(), name='user-profile'),
    path('api/token/refresh/', CustomTokenRefreshView.as_view(), name='token_refresh'),
    path('user-profile/verify-update/', UserProfileVerifyUpdateView.as_view(), name='user-profile-verify-update'),
    path('password-reset/', PasswordResetRequestView.as_view(), name='password_reset_request'),
    path('reset/<uidb64>/', PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('wishlists/', WhishlistCreateView.as_view(), name='list_wishlists'),
    path('wishlist/add/<int:pk>/', WhishlistCreateView.as_view(), name='wishlist-add'),
    path('wishlist/delete/<int:pk>/', WhishlistDeleteView.as_view(), name='whishlist-delete'),
    path('cart/detail/', CartItemListCreateView.as_view(), name='cart-item-list-create'),  
    path('cart/detail/<int:pk>/', CartItemListCreateView.as_view(), name='cart-item-list-create'),  
    path('cart/<int:pk>/', CartItemDetailView.as_view(), name='cart-item-detail'),  
    path('addresses/', AddressViewSet.as_view({'get': 'list', 'post': 'create'}), name='address-list'),
    path('addresses/<int:pk>/', AddressViewSet.as_view({'get': 'retrieve', 'put': 'update', 'patch': 'partial_update', 'delete': 'destroy'}), name='address-detail'),
]
