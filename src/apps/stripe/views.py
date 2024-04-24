from django.views import View
from django.shortcuts import render, get_object_or_404
from src.administration.admins.models import Order

from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator

from src.apps.stripe.bll import (stripe_checkout_create, checkout_payment_success, checkout_payment_failed
                                 )
import stripe

""" WEBSITE CHECKOUT -------------------------------------------------------------------------------------- """

STRIPE_PUBLIC_KEY = "pk_test_51KNUx8GWh1G1v77h4cAKDbEvH3wEbK4yVZfSGKT5f5wgShK8cipV0ctpNrZ2tqt63fsVmJp4sAk6cs8mogGlzHlL00CTKGtGvE"
STRIPE_SECRET_KEY = "sk_test_51KNUx8GWh1G1v77hDR40VBVDDZTK2pgUZMk0yxDyN4evl4lBg2LyxFyOQCDoLQWhgy1t9bAzcC63c681rUe5mxtv00vHfKyh2r"


def create_stripe_checkout_session(request, order):
    stripe.api_key = STRIPE_SECRET_KEY
    host = request.get_host()
    session = stripe_checkout_create(request, order, host)
    return session.url


class StripeSuccessView(View):
    def get(self, request, *args, **kwargs):
        stripe_id = self.request.GET.get('session_id')
        order = get_object_or_404(Order, stripe_id=stripe_id)
        checkout_payment_success(stripe_id, order)
        return render(self.request, 'stripe/success.html')


@method_decorator(login_required, name='dispatch')
class StripeCancelView(View):
    def get(self, request, *args, **kwargs):
        stripe_id = self.request.GET.get('session_id')
        checkout_payment_failed(stripe_id)
        return render(request, 'stripe/cancelled.html')


""" VENDOR VIEWS FOR STRIPE -------------------------------------------------------------------------------------- """
