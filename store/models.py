from django.db import models
from courses.models import ModelTrackeBaseClass
from cloudinary.models import CloudinaryField

class ProductCategories(ModelTrackeBaseClass):
    name = models.CharField(max_length=50, unique=True)

    def __str__(self) -> str:
        return self.name
        
class ProductSubCategories(ModelTrackeBaseClass):
    name = models.CharField(max_length=50)
    category =  models.ForeignKey(ProductCategories, on_delete=models.CASCADE, related_name='subcategories')

    def __str__(self) -> str:
        return self.name

class Products(ModelTrackeBaseClass):
    name = models.CharField(max_length=100, unique=True)
    sub_category = models.ForeignKey(ProductSubCategories, related_name='products', on_delete=models.CASCADE)
    description = models.TextField(blank=True, null=True)
    is_active = models.BooleanField(default=True)

    def __str__(self) -> str:
        return self.name

class ProductImages(ModelTrackeBaseClass):
    product = models.ForeignKey('ProductDetails', related_name='images', on_delete=models.CASCADE)
    image = CloudinaryField('image', folder='product_images/')

class ProductDetails(ModelTrackeBaseClass):
    product = models.ForeignKey(Products, related_name='details', on_delete=models.CASCADE)
    size = models.CharField(max_length=50, null=True, blank=True)
    color = models.CharField(max_length=50, null=True, blank=True)
    stock = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)


