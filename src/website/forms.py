from django.forms import ModelForm

from src.administration.admins.models import Order


class OrderForm(ModelForm):
    class Meta:
        model = Order
        fields = ['name', 'email', 'phone', 'country', 'city', 'street_address', 'postal_code']