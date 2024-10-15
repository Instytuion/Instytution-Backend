from django.contrib import admin
from .models import ProductCategories, Products, ProductImages, ProductDetails

# Admin for Product Categories
@admin.register(ProductCategories)
class ProductCategoriesAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')  
    search_fields = ('name',)     

# Admin for Products
@admin.register(Products)
class ProductsAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'category',)  
    search_fields = ('name',)                            
    list_filter = ('category',)                          
    autocomplete_fields = ('category',)      

# Admin for Product Images
@admin.register(ProductImages)
class ProductImagesAdmin(admin.ModelAdmin):
    list_display = ('id', 'product', 'image') 
    search_fields = ('product__name',)         

# Admin for Product Details
@admin.register(ProductDetails)
class ProductDetailsAdmin(admin.ModelAdmin):
    list_display = ('id', 'product', 'size', 'color', 'stock')  
    search_fields = ('product__name',)                          
    list_filter = ('size', 'color')                             
