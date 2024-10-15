from rest_framework import generics
from store.serializers import ProductSerializer
from store.models import Products
from accounts.permissions import IsShopAdmin
from rest_framework.permissions import AllowAny
class ProductsListCreateApiView(generics.ListCreateAPIView):
    serializer_class = ProductSerializer

    def get_queryset(self):
        category_name = self.kwargs['category']
        queryset = Products.objects.filter(category__name__iexact=category_name)
        return queryset
    
    def get_permissions(self):
        if self.request.method == 'POST':
            return [IsShopAdmin()]
        else:
            return [AllowAny()]
    
