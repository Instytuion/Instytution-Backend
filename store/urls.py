from django.urls import path
from .views import *


urlpatterns = [
    path('list-sub-categories/<str:category>', SubCategoryListAPIView.as_view(), name='list-sub-categories'),     
]