from django.forms import ModelForm

from src.administration.admins.models import Order


class OrderCheckoutForm(ModelForm):
    class Meta:
        model = Order
        fields = [
            'full_name', 'contact', 'postal_code', 'address', 'city',
            'state', 'country', 'payment_type'
        ]