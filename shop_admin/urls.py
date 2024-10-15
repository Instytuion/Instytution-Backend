from django.urls import path
from .views import *


urlpatterns = [
    path('list-create/<str:category>',ProductsListCreateApiView.as_view(), name='product-list-create'),     
]