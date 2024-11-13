from rest_framework import generics, status
from .models import ProductSubCategories
from .serializers import *
from rest_framework.exceptions import NotFound

class SubCategoryListAPIView(generics.ListAPIView):
    """
    API endpoint that returns a list of subcategories according  to the category.
    """
    serializer_class = ProductSubCategorySerializer
    
    def get_queryset(self):
        category_name = self.kwargs['category']
        try:
            category = ProductCategories.objects.get(name__iexact=category_name)
        except ProductCategories.DoesNotExist:
            raise NotFound("Category not found", code=status.HTTP_404_NOT_FOUND)
        
        queryset = ProductSubCategories.objects.filter(category=category)
        
        if not queryset:
            raise NotFound("No subcategories found for this category",code=status.HTTP_404_NOT_FOUND)

        return queryset