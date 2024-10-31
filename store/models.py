from django.db import models
from courses.models import ModelTrackeBaseClass
from cloudinary.models import CloudinaryField
from django.db.models import Avg

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
    
    @property
    def average_rating(self):
        avg_rating = self.ratings.aggregate(Avg('rating')).get('rating__avg')
        return avg_rating if avg_rating is not None else 0

    @property
    def rating_count(self):
        return self.ratings.count()

class ProductImages(ModelTrackeBaseClass):
    product = models.ForeignKey(Products, related_name='images', on_delete=models.CASCADE)
    color = models.CharField(max_length=50, null=True, blank=True)  
    image = CloudinaryField('image', folder='product_images/')
    

class ProductDetails(ModelTrackeBaseClass):
    product = models.ForeignKey(Products, related_name='details', on_delete=models.CASCADE)
    size = models.CharField(max_length=50, null=True, blank=True)
    color = models.CharField(max_length=50, null=True, blank=True)
    stock = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['product', 'size', 'color'], name='unique_product_detail')
        ]

    def  __str__(self) -> str:
        return f"{self.product.name} - {self.color} - {self.size}"


