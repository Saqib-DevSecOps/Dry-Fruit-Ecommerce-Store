from django import forms
from django.forms import ModelForm

from .models import (
    Product, ProductImage, Blog, ProductWeight, PickupLocation, ProductSize
)
from ...accounts.models import User


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = [
            'sku', 'thumbnail_image', 'title', 'category', 'manufacturer_brand',
            'tags', 'description', 'video_link',
            'promotional', 'price', 'quantity', 'discount',
        ]


class ProductImageForm(forms.ModelForm):
    class Meta:
        model = ProductImage
        fields = [
            'image',
        ]


class ProductWeightForm(forms.ModelForm):
    class Meta:
        model = ProductWeight
        fields = [
            'weight', 'price'
        ]


class ProductSizeForm(forms.ModelForm):
    class Meta:
        model = ProductSize
        fields = [
            'length', 'breadth', 'height', 'weight'
        ]


class MyProfileForm(ModelForm):
    class Meta:
        model = User
        fields = [
            'profile_image', 'first_name', 'last_name',
            'phone_number', 'email'
        ]


class ShipRocketShipmentForm(forms.Form):
    pickup_location = forms.ModelChoiceField(queryset=PickupLocation.objects.all(), required=True,
                                             help_text="The name of the pickup location added in your Shiprocket "
                                                       "account. This cannot be a new location.")
    length = forms.DecimalField(max_digits=10, decimal_places=2, required=True,
                                help_text="The length of the item in cms. Must be more than 0.5.")
    breadth = forms.DecimalField(max_digits=10, decimal_places=2, required=True,
                                 help_text="The breadth of the item in cms. Must be more than 0.5.")
    height = forms.DecimalField(max_digits=10, decimal_places=2, required=True,
                                help_text="The height of the item in cms. Must be more than 0.5.")
    weight = forms.DecimalField(max_digits=10, decimal_places=2, required=True,
                                help_text="The weight of the item in kgs. Must be more than 0.")
