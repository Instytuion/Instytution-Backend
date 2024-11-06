from rest_framework import serializers
from .models import Products, ProductImages, ProductDetails, ProductCategories, ProductSubCategories
from django.db import transaction
from rest_framework.exceptions import ValidationError
from django.core.exceptions import ObjectDoesNotExist
from accounts.models import RatingImage,Rating


class ProductSubCategorySerializer(serializers.ModelSerializer):
    category_name =  serializers.CharField(source='category.name', required=False)

    class Meta:
        model = ProductSubCategories
        fields = ['name', 'category_name']
        extra_kwargs = {
            'name': {'required': True}  
        }
        
    def create(self, validated_data):
        request = self.context.get('request')
        category_name = validated_data.pop('category', {}).get('name')
        
        if not category_name:
            raise  ValidationError({'category_name': 'Category name is required.'})

        
        try:
            category = ProductCategories.objects.get(name=category_name)
        except ObjectDoesNotExist:
            raise serializers.ValidationError(f"Category '{category_name}' does not exist.")
        
        validated_data['category'] = category
        validated_data['created_by'] = request.user 
        validated_data['updated_by'] = request.user 
        
        return super().create(validated_data)

    def update(self, instance, validated_data):
        request = self.context.get('request')
        category_name = validated_data.pop('category', {}).get('name')
        if category_name:
            try:
                category = ProductCategories.objects.get(name=category_name)
            except ObjectDoesNotExist:
                raise serializers.ValidationError(f"Category '{category_name}' does not exist.")
            instance.category = category
            instance.updated_by = request.user
        return super().update(instance, validated_data)

class ProductImagesSerializer(serializers.ModelSerializer):
    image =  serializers.ImageField(use_url=True,)
    
    class Meta:
        model = ProductImages
        fields = [ 'id','image', 'color']
        
    def create(self, validated_data):
        request = self.context.get('request')
        product_id = request.parser_context['kwargs'].get('pk') 
        
        try:
            product = Products.objects.get(id=product_id)
        except ObjectDoesNotExist:
             raise serializers.ValidationError(f"Product with id {product_id} does not exist.")
        validated_data['product'] = product
        validated_data['created_by'] = request.user
        validated_data['updated_by'] = request.user
        return super().create(validated_data)

class ProductDetailsSerializer(serializers.ModelSerializer):

    class Meta:
        model = ProductDetails
        fields = [
            'id', 'size', 'price', 'color', 'stock', 'price',
        ]


class RatingImageSerializer(serializers.ModelSerializer):
    image =  serializers.ImageField(use_url=True,)
    class Meta:
        model = RatingImage
        fields = ['id', 'image']



class RatingSerializer(serializers.ModelSerializer):
    rating_images = RatingImageSerializer(many=True, read_only=True)  

    class Meta:
        model = Rating
        fields = ['id', 'product', 'user', 'rating', 'feedback', 'created_at', 'rating_images']

class ProductSerializer(serializers.ModelSerializer):
    sub_category = ProductSubCategorySerializer()  
    details = ProductDetailsSerializer(many=True)
    images = ProductImagesSerializer(many=True,) 
    ratings = RatingSerializer(many=True, read_only=True)   
    average_rating = serializers.FloatField( read_only=True)
    rating_count = serializers.IntegerField( read_only=True)
    class Meta:
        model = Products
        fields = [
            'id', 'name', 'sub_category', 'description', 'is_active', 'details', 'images', 'ratings','average_rating', 'rating_count',
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
    
    def update(self, instance, validated_data):
        request = self.context.get('request')
        print('request.data...........',request.data)

        sub_category_data = validated_data.pop('sub_category', None)
        if sub_category_data:
            sub_category_name = sub_category_data.get('name')
            try:
                sub_category = ProductSubCategories.objects.get(name=sub_category_name)
                instance.sub_category = sub_category
            except ProductSubCategories.DoesNotExist:
                raise ValidationError(f"Sub-category '{sub_category_name}' does not exist.")

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.updated_by = request.user

        instance.save()
        
        return instance

