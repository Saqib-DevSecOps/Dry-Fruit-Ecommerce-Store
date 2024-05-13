import django_filters
from django import forms
from django.forms import TextInput

from src.accounts.models import User
from src.administration.admins.models import Product, Order, Blog
from src.apps.shipment.models import ShipmentOrder


class UserFilter(django_filters.FilterSet):
    username = django_filters.CharFilter(widget=TextInput(attrs={'placeholder': 'username'}), lookup_expr='icontains')
    email = django_filters.CharFilter(widget=TextInput(attrs={'placeholder': 'email'}), lookup_expr='icontains')

    class Meta:
        model = User
        fields = {'is_active', 'is_client'}


class ProductFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(widget=TextInput(attrs={'placeholder': 'Name'}), lookup_expr='icontains')

    class Meta:
        model = Product
        fields = {'title', 'category'}


class OrderFilter(django_filters.FilterSet):
    user = django_filters.CharFilter(widget=TextInput(attrs={'placeholder': 'User'}), lookup_expr='icontains')

    class Meta:
        model = Order
        fields = {'payment_status', 'order_status'}


class BlogFilter(django_filters.FilterSet):
    title = django_filters.CharFilter(widget=TextInput(attrs={'placeholder': 'User'}), lookup_expr='icontains')
    author = django_filters.CharFilter(widget=TextInput(attrs={'placeholder': 'Author'}), lookup_expr='icontains')

    class Meta:
        model = Blog
        fields = {'status'}


class ShipmentOrderFilter(django_filters.FilterSet):
    user = django_filters.CharFilter(widget=TextInput(attrs={'placeholder': 'User'}), lookup_expr='icontains')

    payment_status = django_filters.CharFilter(
        field_name='payment_status',
        widget=forms.TextInput(attrs={'placeholder': 'payment-status'}),
        lookup_expr='icontains'
    )

    customer_email = django_filters.CharFilter(
        field_name='customer_email',
        widget=forms.TextInput(attrs={'placeholder': 'customer-email'}),
        lookup_expr='icontains'
    )

    class Meta:
        model = ShipmentOrder
        fields = ['payment_status', 'customer_email']
