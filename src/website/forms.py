from django import forms
from django.core.exceptions import ValidationError
from django.forms import ModelForm

from src.administration.admins.models import Order


class OrderCheckoutForm(ModelForm):
    class Meta:
        model = Order
        fields = [
            'full_name', 'contact', 'country', 'state', 'city',
            'address', 'address_label', 'postal_code',
            'gst_in', 'shipment_type', 'service_type'
        ]

    def clean_shipment_type(self):
        shipment_type = self.cleaned_data.get('shipment_type')
        if shipment_type not in ['custom', 'ship_rocket']:
            raise ValidationError('Please select a valid shipment type (Custom or Ship Rocket).')
        return shipment_type


class CouponApplyForm(forms.Form):
    code = forms.CharField(max_length=350)
