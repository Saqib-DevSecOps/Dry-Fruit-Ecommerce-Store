import django_filters
from django import forms
from django.db.models import Q

from src.administration.admins.models import Product, Order


class ProductFilter(django_filters.FilterSet):
    title = django_filters.CharFilter(field_name='title', lookup_expr='icontains', label="Title")
    min_price = django_filters.NumberFilter(field_name='price', lookup_expr='gte', label="Min Price")
    max_price = django_filters.NumberFilter(field_name='price', lookup_expr='lte', label="Max Price")
    ratings = django_filters.MultipleChoiceFilter(
        choices=[
            ('5', '5'),
            ('4', '4'),
            ('3', '3'),
            ('2', '2'),
            ('1', '1'),
            ('0', '0'),
        ],
        widget=forms.CheckboxSelectMultiple(attrs={'class': 'shop-widget-checkbox'}),
        method='filter_by_rating',
        label="Rating"
    )

    class Meta:
        model = Product
        fields = ['title', 'category', 'min_price', 'max_price', 'ratings', 'promotional', 'tags']

    def filter_by_rating(self, queryset, name, value):
        selected_ratings = [int(val) for val in value]
        filters = Q()

        for rating in selected_ratings:
            if rating == 5:
                filters |= Q(average_review__gte=5)
            elif rating == 4:
                filters |= Q(average_review__gte=4, average_review__lt=5)
            elif rating == 3:
                filters |= Q(average_review__gte=3, average_review__lt=4)
            elif rating == 2:
                filters |= Q(average_review__gte=2, average_review__lt=3)
            elif rating == 1:
                filters |= Q(average_review__gte=1, average_review__lt=2)
            elif rating == 0:
                filters |= Q(average_review__isnull=True) | Q(average_review=0)

        if filters:
            queryset = queryset.filter(filters)
        return queryset


class OrderFilter(django_filters.FilterSet):
    class Meta:
        model = Order
        fields = {'payment_type', 'order_status', 'payment_status'}