from django.forms import ModelForm
from src.accounts.models import User, Address


class UserProfileForm(ModelForm):
    class Meta:
        model = User
        fields = [
            'profile_image', 'first_name', 'last_name',
            'phone_number'
        ]


class AddressForm(ModelForm):
    class Meta:
        model = Address
        fields = "__all__"
        exclude = ['user', ]
