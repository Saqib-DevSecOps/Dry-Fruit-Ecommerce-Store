from django.urls import path
from .views import (
    StripeCancelView, StripeSuccessView,create_stripe_checkout_session,
)


app_name = 'stripe'
urlpatterns = [

    path('checkout/<int:order_id>/', create_stripe_checkout_session, name='checkout'),
    path('stripe/success/', StripeSuccessView.as_view(), name='success'),
    path('stripe/cancel/', StripeCancelView.as_view(), name='cancel'),

]