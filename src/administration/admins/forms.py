from django import forms
from django.forms import ModelForm

from .models import (
    Product, ProductImage, Blog
)
from ...accounts.models import User


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = [
            'thumbnail_image', 'title',
            'category',
            'description', 'is_active'
        ]


class ProductImageForm(forms.ModelForm):
    class Meta:
        model = ProductImage
        fields = [
            'image',
        ]


class MyProfileForm(ModelForm):
    class Meta:
        model = User
        fields = [
            'profile_image', 'first_name', 'last_name',
            'phone_number', 'email'
        ]
