from django.core.exceptions import ValidationError
from django.forms import ModelForm

from src.administration.admins.models import Order


class OrderCheckoutForm(ModelForm):
    class Meta:
        model = Order
        fields = [
            'full_name', 'contact', 'postal_code', 'address', 'address_label', 'city',
            'state', 'country',  'shipment_type', 'service_type'
        ]

    def clean_shipment_type(self):
        shipment_type = self.cleaned_data.get('shipment_type')
        if shipment_type not in ['custom', 'ship_rocket']:
            raise ValidationError('Please select a valid shipment type (Custom or Ship Rocket).')
        return shipment_type
