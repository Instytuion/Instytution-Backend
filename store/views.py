from rest_framework import generics
from .models import ProductSubCategories
from .serializers import *

class SubCategoryListAPIView(generics.ListAPIView):
    serializer_class = ProductSubCategorySerializer
    queryset = ProductSubCategories.objects.all()
    
    
    
