from dj_rest_auth.registration.serializers import RegisterSerializer
from django.contrib.auth import get_user_model
from django.db import transaction
from rest_framework import serializers


class RegisterSerializerRestAPI(RegisterSerializer):
    # profile_image = serializers.ImageField(max_length=None, allow_empty_file=False, use_url=True)

    @transaction.atomic
    def save(self, request):
        if self.data.get('email'):
            if get_user_model().objects.filter(email=self.data.get('email')).exists():
                raise serializers.ValidationError('Email already exists')

        # user.profile_image = self.data.get('profile_image')
        user = super().save(request)
        return user

    def validate_email(self, email):
        return super().validate_email(self.data.get('email'))
