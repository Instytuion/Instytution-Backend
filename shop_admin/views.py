from rest_framework import generics, filters
from store.serializers import ProductSerializer
from store.models import Products
from accounts.permissions import IsShopAdmin , IsAdminAndAuthenticated
from rest_framework.permissions import AllowAny
from django_filters.rest_framework import DjangoFilterBackend
from store.filters import ProductFilter
from rest_framework.serializers import ValidationError
from rest_framework.exceptions import NotFound
from store.serializers import *
from  store.models import ProductSubCategories
from accounts.serializers import ProductSpecificDetailSerializer
from .utils import restructure_product_creation_data
from  rest_framework import status
from rest_framework.response import Response
from custom_admin.pagination import StandardResultsSetPagination
import cloudinary.uploader




class ProductsListCreateApiView(generics.ListCreateAPIView):
    # pagination_class = StandardResultsSetPagination
    serializer_class = ProductSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_class = ProductFilter
    search_fields = ['name', 'description', 'sub_category__name', 'sub_category__category__name']  


    def get_queryset(self):
        category_name = self.kwargs['category']
        
        if not ProductCategories.objects.filter(name__iexact=category_name).exists():
            raise ValidationError({"error": f"Category '{category_name}' does not exist."})
        
        queryset = Products.objects.filter(sub_category__category__name__iexact=category_name)
        filtered_qs = ProductFilter(self.request.GET, queryset=queryset).qs

        return filtered_qs.distinct()
        
        
    
    def get_permissions(self):
        if self.request.method == 'POST':
            return [IsShopAdmin()]
        else:
            return [AllowAny()]
    
    def post(self, request, *args, **kwargs):
        print("Entered in post method")
        product_data = restructure_product_creation_data(request.data)
        print("Product Data: ", product_data)
        serializer = self.get_serializer(data=product_data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response(serializer.data, status=201)


class ProductGetandUpdate(generics.RetrieveUpdateAPIView):
    
    serializer_class = ProductSerializer
    
    def get_permissions(self):
        if self.request.method == 'PATCH':
            return [IsShopAdmin()]
        else:
            return [AllowAny()]
        
    def get_object(self):
        try:
            product = Products.objects.get(id=self.kwargs['pk'])
        except Products.DoesNotExist:
            raise NotFound(detail="Product not found", code=404)
        
        return product
    
class ProductSubCategoryCreateApiView(generics.CreateAPIView):
    serializer_class = ProductSubCategorySerializer
    permission_classes = [IsShopAdmin]
    
class productSubcategoryRetriveUpdateApiView(generics.RetrieveUpdateAPIView):
    serializer_class =  ProductSubCategorySerializer
    permission_classes = [IsShopAdmin]
    
    def get_queryset(self):
        return ProductSubCategories.objects.filter(id=self.kwargs['pk'])


class ProductSpecificDetailCreateView(generics.CreateAPIView):
    """
    This view is used to create a new product detail.
    """
    permission_classes = [IsShopAdmin]
    serializer_class = ProductSpecificDetailSerializer
    
class ProductDetailRetrieveUpdateView(generics.RetrieveUpdateAPIView):
    """
    This view is used to retrieve and update a product detail.
    """
    serializer_class = ProductSpecificDetailSerializer
    permission_classes = [IsShopAdmin]

    def get_object(self):
        product_detail_id = self.kwargs.get('pk')
        try:
            return ProductDetails.objects.get(id=product_detail_id)
        except ProductDetails.DoesNotExist:
            raise NotFound("Product Detail does not exist")
        
class ProductImageRetriveUpdateDeleteView(generics.RetrieveUpdateDestroyAPIView):
    """
    This view is used to retrieve, update and delete a product image.
    """
    permission_classes = [IsShopAdmin]
    serializer_class = ProductImagesSerializer
    
    def get_queryset(self):
        return ProductImages.objects.filter(id=self.kwargs['pk'])
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        
        public_id = instance.image.public_id  
        cloudinary.uploader.destroy(public_id)

        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)
    
class ProductImagesListCreateView(generics.ListCreateAPIView):
    permission_classes =  [IsShopAdmin]
    serializer_class = ProductImagesSerializer
    
    def get_queryset(self):
        try:
            product_id = self.kwargs['pk']
            queryset = ProductImages.objects.filter(product=product_id)

            if not queryset.exists():
                raise NotFound(detail="No images found for this product.")

            return queryset
        except KeyError:
            raise NotFound(detail="Product ID not found.")
    

     

from datetime import datetime, timedelta
from payments.models import CoursePayment
from django.db.models.functions import TruncDate
from django.db.models import Count
from course_admin.serializers import PurchaseReportSerializer
from order.models import OrderItem
from rest_framework.views import APIView
from django.db.models import Sum

class StorePurchaseReportApiVeiw(APIView):
    """
    To get the purchase report of Store in a Month
    """
    permission_classes = [IsShopAdmin | IsAdminAndAuthenticated]

    def post(self, request):
        serializer = PurchaseReportSerializer(data=request.data)
        if serializer.is_valid():
            year = serializer.validated_data['year']
            month = serializer.validated_data['month']
        
            start_date = datetime(year, month, 1).date()
            if month == 12:
                end_date = (datetime(year + 1, 1, 1) - timedelta(days=1)).date()
            else:
                end_date = (datetime(year, month + 1, 1) - timedelta(days=1)).date()

            date_quantity_map = (
                OrderItem.objects
                .select_related('order')
                .filter(order__created_at__date__range=(start_date, end_date))
                .annotate(order_date=TruncDate('order__created_at'))
                .values('order_date')
                .annotate(
                    total_quantity=Sum('quantity'),
                )
                .order_by('order_date')
            )
            
            date_count_map = {date: 0 for date in [start_date + timedelta(days=i) for i in range((end_date - start_date).days + 1)]}
            
            for record in date_quantity_map:
                date_count_map[record['order_date']] = record['total_quantity']

            # Convert to a list of dictionaries for the response
            response_data = [{'date': date, 'count': count} for date, count in date_count_map.items()]

            return Response({
                "start_date": start_date,
                "end_date": end_date,
                "purchase_report": response_data
            }, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)