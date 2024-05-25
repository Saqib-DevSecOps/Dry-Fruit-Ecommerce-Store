from allauth.socialaccount.providers.facebook.views import FacebookOAuth2Adapter
from allauth.socialaccount.providers.google.views import GoogleOAuth2Adapter
from allauth.socialaccount.providers.oauth2.client import OAuth2Client
from dj_rest_auth.registration.views import SocialLoginView
from rest_framework.authtoken.models import Token

from core.settings import GOOGLE_CALLBACK_ADDRESS


class GoogleLoginView(SocialLoginView):
    adapter_class = GoogleOAuth2Adapter
    callback_url = GOOGLE_CALLBACK_ADDRESS
    client_class = OAuth2Client

    def get_response(self):
        response = super().get_response()
        token, created = Token.objects.get_or_create(user=self.user)
        response.data['token'] = token.key
        return response


class FacebookLogin(SocialLoginView):
    adapter_class = FacebookOAuth2Adapter
