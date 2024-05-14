from django.urls import path, include

from .views import (
    GoogleLoginView,FacebookLogin
)

app_name = 'accounts'
urlpatterns = [
    path("google/login/", GoogleLoginView.as_view(), name="google_login"),
    path("facebook/login/", GoogleLoginView.as_view(), name="facebook_login")
]