from django import forms
from django.forms import ModelForm

from .models import (
    Product, ProductImage, Blog, ProductWeight
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
            'weight','price'
        ]


class MyProfileForm(ModelForm):
    class Meta:
        model = User
        fields = [
            'profile_image', 'first_name', 'last_name',
            'phone_number', 'email'
        ]
