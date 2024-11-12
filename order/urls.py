from django.urls import path
from .views import CreateOrderView , VerifyOrderView 

urlpatterns = [
    path('create-order/', CreateOrderView.as_view(), name='create_order'),  
    path('verify-order/', VerifyOrderView.as_view(), name='verify_order'),  
]
