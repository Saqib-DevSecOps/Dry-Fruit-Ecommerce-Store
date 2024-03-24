from django.urls import path, include
from .views import LogoutView, CrossAuthView

app_name = 'accounts'
urlpatterns = [
    path('logout/', LogoutView.as_view(), name='logout'),
    path('cross-auth/', CrossAuthView.as_view(), name='cross-auth')
]


