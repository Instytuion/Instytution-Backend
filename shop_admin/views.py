from rest_framework import generics, filters
from store.serializers import ProductSerializer
from store.models import Products
from accounts.permissions import IsShopAdmin
from rest_framework.permissions import AllowAny
from django_filters.rest_framework import DjangoFilterBackend
from store.filters import ProductFilter
from rest_framework.serializers import ValidationError
from rest_framework.exceptions import NotFound



class ProductsListCreateApiView(generics.ListCreateAPIView):
    serializer_class = ProductSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_class = ProductFilter
    search_fields = ['name', 'description', 'sub_category__name', 'sub_category__category__name']  


    def get_queryset(self):
        category_name = self.kwargs['category']
        queryset = Products.objects.filter(sub_category__category__name__iexact=category_name)
        
        filtered_qs = ProductFilter(self.request.GET, queryset=queryset).qs

        # Return distinct products
        if not filtered_qs.exists():
            raise ValidationError({"error": f"Category '{category_name}' does not exist or has no products."})
        
        return filtered_qs.distinct() 
        
        
    
    def get_permissions(self):
        if self.request.method == 'POST':
            return [IsShopAdmin()]
        else:
            return [AllowAny()]
    
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