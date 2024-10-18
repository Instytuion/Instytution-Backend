from django.contrib import admin
from .models import ProductCategories, Products, ProductImages, ProductDetails, ProductSubCategories

# Admin for Product Categories
@admin.register(ProductCategories)
class ProductCategoriesAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')  
    search_fields = ('name',)     

@admin.register(ProductSubCategories)
class  ProductSubCategoriesAdmin(admin.ModelAdmin):
    list_display = ('id', 'name',  'category')  
    search_fields = ('name',)

# Admin for Products
@admin.register(Products)
class ProductsAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'sub_category',)  
    search_fields = ('name',)                            
    list_filter = ('sub_category',)                          
    autocomplete_fields = ('sub_category',)      

# Admin for Product Images
@admin.register(ProductImages)
class ProductImagesAdmin(admin.ModelAdmin):
    list_display = ('id', 'product', 'image', 'color') 
    search_fields = ('product__name',)         

# Admin for Product Details
@admin.register(ProductDetails)
class ProductDetailsAdmin(admin.ModelAdmin):
    list_display = ('id', 'product', 'size', 'color', 'stock')  
    search_fields = ('product__name',)                          
    list_filter = ('size', 'color')                             
