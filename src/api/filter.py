import django_filters
from django_filters import FilterSet, CharFilter, NumberFilter

from src.administration.admins.models import Product, Blog


class ProductFilter(FilterSet):
    search = CharFilter(field_name='name', lookup_expr='icontains')
    price_min = NumberFilter(field_name='price', lookup_expr='gte')
    price_max = NumberFilter(field_name='price', lookup_expr='lte')

    class Meta:
        model = Product
        fields = ['search', 'price_min', 'price_max']


class BlogFilter(django_filters.FilterSet):
    title = django_filters.CharFilter(lookup_expr='icontains')
    category = django_filters.CharFilter(field_name='category__name', lookup_expr='icontains')

    class Meta:
        model = Blog
        fields = ['title', 'category']