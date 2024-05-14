
from django.contrib import admin
from django.shortcuts import render
from django.urls import path, include, re_path
from django.views.static import serve
from django.views.generic import TemplateView
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework import permissions

from core.settings import  MEDIA_ROOT, STATIC_ROOT
schema_view = get_schema_view(
    openapi.Info(
        title="Ecommerce Site",
        default_version="1.0",
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)


def handler404(request, *args, **kwargs):
    return render(request, "404.html")


def handler500(request, *args, **kwargs):
    return render(request, "500.html")


# EXTERNAL APPS URLS
urlpatterns = [

    # DJANGO URLS > remove in extreme security
    path('admin/', admin.site.urls),

    # SWAGGER
    re_path(r'^api(?P<format>\.json|\.yaml)$', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    re_path(r'^api$', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    re_path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),

    # REST-AUTH URLS
    re_path('rest-auth/registration/', include('dj_rest_auth.registration.urls')),
    re_path('rest-auth/', include('dj_rest_auth.urls')),
]


# universal urls
urlpatterns += [
    path('under-construction/', TemplateView.as_view(template_name='000.html')),

]

# your apps urls
urlpatterns += [
    # path('', include('src.website.urls', namespace='website')),
    path('accounts/', include('src.accounts.urls', namespace='accounts')),
    path('admins/', include('src.administration.admins.urls', namespace='admins')),
    path('', include('src.website.urls', namespace='website')),
    path('api/', include('src.api.urls', namespace='api')),
    path('razorpay/', include('src.apps.razorpay.urls', namespace='razorpay')),
    path('c/', include('src.administration.client.urls', namespace='client')),
    path('accounts/', include('allauth.urls')),
    path('payment/', include('src.apps.stripe.urls', namespace='stripe')),

]

urlpatterns += [
    path('tinymce/', include('tinymce.urls')),
]

urlpatterns += [
    re_path(r'^media/(?P<path>.*)$', serve, {'document_root': MEDIA_ROOT}),
    re_path(r'^static/(?P<path>.*)$', serve, {'document_root': STATIC_ROOT}),
]
