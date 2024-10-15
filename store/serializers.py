from rest_framework import serializers
from .models import Products, ProductImages, ProductDetails, ProductCategories
from django.db import transaction
from rest_framework.exceptions import ValidationError
from django.core.exceptions import ObjectDoesNotExist

class ProductImagesSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImages
        fields = ['image']

class ProductDetailsSerializer(serializers.ModelSerializer):
    images = ProductImagesSerializer(many=True,)  

    class Meta:
        model = ProductDetails
        fields = [
            'id', 'size', 'price', 'color', 'stock', 'price', 'images'
        ]

class ProductSerializer(serializers.ModelSerializer):
    category = serializers.CharField(source='category.name')  
    details = ProductDetailsSerializer(many=True)  

    class Meta:
        model = Products
        fields = [
            'id', 'name', 'category', 'description', 'is_active', 'details'
        ]

    def create(self, validated_data): 
        with transaction.atomic():
            category_data = validated_data.pop('category')
            category_name = category_data.get('name')
            print('category name,  ', category_name)
            details_data = validated_data.pop('details', []) 
            print("details_data", details_data)

            request = self.context.get('request')
            validated_data['created_by'] = request.user
            validated_data['updated_by'] = request.user

            try:
                print('reached in category checking', category_name)
                category = ProductCategories.objects.filter(name=category_name).first()
                print('category,  ', category)

            except ProductCategories.DoesNotExist:
                raise ValidationError(f"Category '{category_name}' does not exist.")

            product = Products.objects.create(
                category=category,
                **validated_data
            )
            
            print('product created')
            
            for detail_data in details_data:
                images_data = detail_data.pop('images', [])

                product_detail =  ProductDetails.objects.create(
                    product=product,
                    created_by=request.user,
                    updated_by=request.user, 
                    **detail_data
                )
                if images_data:
                    for image_data in images_data:
                        ProductImages.objects.create(
                            product=product_detail,
                            created_by=request.user,
                            updated_by=request.user, 
                            **image_data
                        )
                        
            print('completed product creation')

                    
        return product


        
