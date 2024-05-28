from django.forms import ModelForm

from src.accounts.models import User
from src.administration.admins.models import Address


class UserProfileForm(ModelForm):
    class Meta:
        model = User
        fields = [
            'profile_image', 'first_name', 'last_name',
            'phone_number', 'date_of_birth', 'gender'
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['gender'].widget.attrs.update({'class': 'form-control'})


class AddressForm(ModelForm):
    class Meta:
        model = Address
        fields = "__all__"
        exclude = ['user', ]
