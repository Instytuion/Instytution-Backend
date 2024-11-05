from django.urls import path
from .views import *


urlpatterns = [
    path('list-create/<str:category>',ProductsListCreateApiView.as_view(), name='product-list-create'),     
    path('product-get-update/<int:pk>',ProductGetandUpdate.as_view(), name='product-get-update'),     
    path('product/subcategory/create',ProductSubCategoryCreateApiView.as_view(), name='subcategory-create'),     
    path('subcategory/retrive-update/<int:pk>',productSubcategoryRetriveUpdateApiView.as_view(), name='subcategory-retrive-update'),          
    path('product-specific-detail/create/<int:pk>',ProductSpecificDetailCreateView.as_view(), name='product-specific-detail-create'),          
    path('product-specific-detail/get-update/<int:pk>',ProductDetailRetrieveUpdateView.as_view(), name='product-specific-detail-get-update'),          
    path('product-images/get-update-delete/<int:pk>',ProductImageRetriveUpdateDeleteView.as_view(), name='product-images-get-update-delete'),          
    path('product-images/list-create/<int:pk>',ProductImagesListCreateView.as_view(), name='product-images-list-create'),          
]