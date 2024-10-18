from rest_framework import serializers
from .models import Products, ProductImages, ProductDetails, ProductCategories, ProductSubCategories
from django.db import transaction
from rest_framework.exceptions import ValidationError
from django.core.exceptions import ObjectDoesNotExist

class ProductSubCategorySerializer(serializers.ModelSerializer):
    category_name =  serializers.CharField(source='category.name', read_only=True)

    class Meta:
        model = ProductSubCategories
        fields = ['name', 'category_name']
        extra_kwargs = {
            'name': {'required': True}  
        }

class ProductImagesSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImages
        fields = ['image', 'color']

class ProductDetailsSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = ProductDetails
        fields = [
            'id', 'size', 'price', 'color', 'stock', 'price'
        ]

class ProductSerializer(serializers.ModelSerializer):
    sub_category = ProductSubCategorySerializer()  
    details = ProductDetailsSerializer(many=True)
    images = ProductImagesSerializer(many=True,)    

    class Meta:
        model = Products
        fields = [
            'id', 'name', 'sub_category', 'description', 'is_active', 'details', 'images'
        ]

    def create(self, validated_data): 
        print('entered in creating product')
        with transaction.atomic():
            
            # Extract sub_category data
            sub_category_data = validated_data.pop('sub_category')
            sub_category_name = sub_category_data.get('name')
            print('category name,  ', sub_category_name)
            
            details_data = validated_data.pop('details', []) 
            print("details_data", details_data)
            
            images_data = validated_data.pop('images', [])

            request = self.context.get('request')
            validated_data['created_by'] = request.user
            validated_data['updated_by'] = request.user

            # Look for existing sub-category by name
            try:
                sub_category = ProductSubCategories.objects.get(name=sub_category_name)
            except ProductSubCategories.DoesNotExist:
                raise ValidationError(f"Sub-category '{sub_category_name}' does not exist.")
            
            # Create the product
            product = Products.objects.create(
                sub_category=sub_category,
                **validated_data
            )
            
            print('product created')
            
            # Create the product details and images
            for detail_data in details_data:

                product_detail =  ProductDetails.objects.create(
                    product=product,
                    created_by=request.user,
                    updated_by=request.user, 
                    **detail_data
                )
                
            if images_data:
                    for img_data in images_data:
                        ProductImages.objects.create(
                            product=product,
                            created_by=request.user,
                            updated_by=request.user, 
                            **img_data
                        )
                        
            print('completed product creation')

                    
        return product

