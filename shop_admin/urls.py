from django.urls import path
from .views import *


urlpatterns = [
    path('list-create/<str:category>',ProductsListCreateApiView.as_view(), name='product-list-create'),     
    path('product-get-update/<int:pk>',ProductGetandUpdate.as_view(), name='product-get-update'),     
]