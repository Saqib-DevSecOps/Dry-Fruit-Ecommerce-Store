from django.core.exceptions import ValidationError
from django.forms import ModelForm
from src.apps.stripe.models import Transfer


class TransferForm(ModelForm):
    class Meta:
        model = Transfer
        fields = [
            "amount",
            "destination",
            "description",
            "metadata",
        ]

    def clean_destination(self):
        destination = self.cleaned_data["destination"]
        if not destination.active:
            raise ValidationError("The selected external account is not active")
        return destination

    def clean_amount(self):
        amount = self.cleaned_data["amount"]
        if amount <= 0:
            raise ValidationError("The amount must be greater than zero")
        return amount
