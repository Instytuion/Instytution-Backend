from django.urls import path
from .views import *

urlpatterns = [
    path('razorpay/create_order/',CreateRazorpayOrderView.as_view() , name='rz_create_order'),
    path('razorpay/create_course_payment/',CreteCoursePaymentView.as_view() , name='rz_create_course_payment'),
]