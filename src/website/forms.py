from django.forms import ModelForm

from src.administration.admins.models import Order


class OrderForm(ModelForm):
    class Meta:
        model = Order
        fields = ['first_name', "last_name", 'email_address', 'phone_number', 'country', 'city', 'state', 'postal_code',
                  'address_line1', 'address_line2']
