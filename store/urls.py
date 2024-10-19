from django.urls import path
from .views import *


urlpatterns = [
    path('list-sub-categories', SubCategoryListAPIView.as_view(), name='list-sub-categories'),     
]