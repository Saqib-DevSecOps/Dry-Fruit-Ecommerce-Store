import django_filters
from django.db.models import Q
from django.forms import TextInput
from django import forms

from src.administration.admins.models import Product, Blog, ProductCategory, ProductTag, BlogCategory
from src.administration.admins.templatetags.custom_tags import get_html_icons, get_html_icons_for_filter


def get_category_choices():
    return [(category.id, category.name) for category in ProductCategory.objects.filter(is_active=True)]


def filter_by_rating(queryset, name, value):
    selected_ratings = [int(val) for val in value]
    filters = Q()

    for rating in selected_ratings:
        if rating == 5:
            filters |= Q(average_review__gte=5)
        if rating == 4:
            filters |= Q(average_review__gte=4) & Q(average_review__lt=5)
        if rating == 3:
            filters |= Q(average_review__gte=3) & Q(average_review__lt=4)
        if rating == 2:
            filters |= Q(average_review__gte=2) & Q(average_review__lt=3)
        if rating == 1:
            filters |= Q(average_review__gte=1) & Q(average_review__lt=2)
        if rating == 0:
            filters |= Q(average_review__isnull=True) | Q(average_review=0)

    if filters:
        queryset = queryset.filter(filters)
    return queryset


def filter_by_discount(queryset, name, value):
    selected_discount = [int(val) for val in value]
    filters = Q()

    for discount in selected_discount:
        if discount == 5:
            filters |= Q(discount__lte=5)
        if discount == 10:
            filters |= Q(discount__gte=5) & Q(discount__lte=10)
        if discount == 15:
            filters |= Q(discount__gte=11) & Q(discount__lte=15)
        if discount == 25:
            filters |= Q(discount__gte=16) & Q(discount__lte=25)
        if discount == 100:
            filters |= Q(discount__gte=26) & Q(discount__lte=100)

    if filters:
        queryset = queryset.filter(filters)
    return queryset


class ProductFilter(django_filters.FilterSet):
    title = django_filters.CharFilter(field_name='title', lookup_expr='gte', label="Product Name")
    min_price = django_filters.NumberFilter(field_name='price', lookup_expr='gte', label="Min Price")
    max_price = django_filters.NumberFilter(field_name='price', lookup_expr='lte', label="Max Price")
    category = django_filters.ModelMultipleChoiceFilter(
        queryset=ProductCategory.objects.all(),
        widget=forms.CheckboxSelectMultiple(attrs={'class': 'name'}),
        label="Category"
    )
    tags = django_filters.ModelMultipleChoiceFilter(
        queryset=ProductTag.objects.all(),
        widget=forms.CheckboxSelectMultiple(attrs={'class': 'shop-widget-checkbox'}),
        label="Tags"
    )
    ratings = django_filters.MultipleChoiceFilter(
        choices=[
            ('5', get_html_icons_for_filter(5)),
            ('4', get_html_icons_for_filter(4)),
            ('3', get_html_icons_for_filter(3)),
            ('2', get_html_icons_for_filter(2)),
            ('1', get_html_icons_for_filter(1)),
            ('0', get_html_icons_for_filter(0))
        ],
        widget=forms.CheckboxSelectMultiple(attrs={'class': 'shop-widget-checkbox'}),
        method='filter_by_rating',
        label="Rating"
    )
    discount = django_filters.MultipleChoiceFilter(
        choices=[
            (5, 'upto 5%'),
            (10, '5% - 10%'),
            (15, '10% - 15%'),
            (25, '15% - 25%'),
            (100, 'More than 25%'),
        ],
        widget=forms.CheckboxSelectMultiple(attrs={'class': 'shop-widget-checkbox'}),
        method='filter_by_discount',
        label="Rating"
    )
    sorting = django_filters.MultipleChoiceFilter(
        choices=[
            (1, 'Popularity'),
            (2, 'Best selling'),
            (3, 'Trending'),
        ],
        widget=forms.CheckboxSelectMultiple(attrs={'class': 'shop-widget-checkbox'}),
        method='filter_by_sorting',
        label="Sort By"
    )
    appliance_price = django_filters.MultipleChoiceFilter(
        choices=[
            (1, 'High to Low'),
            (2, 'Low to High'),
        ],
        widget=forms.CheckboxSelectMultiple(attrs={'class': 'shop-widget-checkbox'}),
        method='filter_by_appliance_price',
        label="Appliance Price"
    )

    class Meta:
        model = Product
        fields = ['title', 'category', 'min_price', 'ratings', 'sorting', 'appliance_price', 'max_price', 'ratings',
                  'promotional', 'tags']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.form.fields['title'].widget.attrs.update(
            {'class': 'form-control form-control-sm', 'placeholder': 'Enter Product Name'})
        self.form.fields['min_price'].widget.attrs.update(
            {'class': 'form-control form-control-sm', 'placeholder': 'Min Price'})
        self.form.fields['max_price'].widget.attrs.update(
            {'class': 'form-control form-control-sm', 'placeholder': 'Max Price'})
        self.form.fields['promotional'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Promotional'})
        for field_name, field in self.form.fields.items():
            field.label = False

    def filter_by_rating(self, queryset, name, value):
        selected_ratings = [int(val) for val in value]
        filters = Q()

        for rating in selected_ratings:
            if rating == 5:
                filters |= Q(average_review__gte=5)
            if rating == 4:
                filters |= Q(average_review__gte=4) & Q(average_review__lt=5)
            if rating == 3:
                filters |= Q(average_review__gte=3) & Q(average_review__lt=4)
            if rating == 2:
                filters |= Q(average_review__gte=2) & Q(average_review__lt=3)
            if rating == 1:
                filters |= Q(average_review__gte=1) & Q(average_review__lt=2)
            if rating == 0:
                filters |= Q(average_review__isnull=True) | Q(average_review=0)

        if filters:
            queryset = queryset.filter(filters)
        return queryset

    def filter_by_sorting(self, queryset, name, value):
        selected_sorting = [int(val) for val in value]
        filters = Q()

        for sorting_option in selected_sorting:
            if sorting_option == 1:
                queryset = queryset.order_by('-total_views')
            elif sorting_option == 2:
                queryset = queryset.order_by('-total_sales')
            elif sorting_option == 3:
                queryset = queryset.order_by('-created_on')

        return queryset.distinct()

    def filter_by_appliance_price(self, queryset, name, value):
        selected_sorting = [int(val) for val in value]
        for sorting_option in selected_sorting:
            if sorting_option == 1:
                queryset = queryset.order_by('-price')
            elif sorting_option == 2:
                queryset = queryset.order_by('price')
        return queryset.distinct()

    def filter_by_discount(self, queryset, name, value):
        selected_discount = [int(val) for val in value]
        filters = Q()

        for discount in selected_discount:
            if discount == 5:
                filters |= Q(discount__lte=5)
            if discount == 10:
                filters |= Q(discount__gte=5) & Q(discount__lte=10)
            if discount == 15:
                filters |= Q(discount__gte=11) & Q(discount__lte=15)
            if discount == 25:
                filters |= Q(discount__gte=16) & Q(discount__lte=25)
            if discount == 100:
                filters |= Q(discount__gte=26) & Q(discount__lte=100)

        if filters:
            queryset = queryset.filter(filters)
        return queryset


def post_filter(queryset, name, value):
    return queryset.filter(Q(title__icontains=value) | Q(content__icontains=value))


class BlogFilter(django_filters.FilterSet):
    category = django_filters.ModelMultipleChoiceFilter(
        queryset=BlogCategory.objects.all(),
        widget=forms.CheckboxSelectMultiple(attrs={'class': 'name'}),
        label="Category"
    )

    class Meta:
        model = Blog
        fields = ['category']
