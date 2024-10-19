import django_filters
from store.models import Products

class ProductFilter(django_filters.FilterSet):
    min_price = django_filters.NumberFilter(field_name="details__price", lookup_expr='gte')
    max_price = django_filters.NumberFilter(field_name="details__price", lookup_expr='lte')
    color = django_filters.CharFilter(field_name="details__color", lookup_expr='iexact')
    size = django_filters.CharFilter(field_name="details__size", lookup_expr='iexact')
    sub_category = django_filters.BaseInFilter(field_name="sub_category__name", lookup_expr='in')

    class Meta:
        model = Products
        fields = ['sub_category', 'is_active']  
