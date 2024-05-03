from django.shortcuts import render, get_object_or_404
import razorpay
from django.conf import settings
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponseBadRequest

from src.administration.admins.models import Order
from src.apps.razorpay.bll import handle_payment

# authorize razorpay client with API Keys.
razorpay_client = razorpay.Client(
    auth=(settings.RAZORPAY_API_KEY, settings.RAZORPAY_API_SECRET))


class CreateRazorPayCheckout(View):

    def get(self, request, *args, **kwargs):
        # todo: need to validate order here

        currency = 'INR'
        amount = 20000  # Rs. 200
        razorpay_order = razorpay_client.order.create(dict(amount=amount,
                                                           currency=currency,
                                                           payment_capture='0'))
        order = self.kwargs.get('pk')
        razorpay_order_id = razorpay_order['id']
        order = get_object_or_404(Order, id=order)
        order.razorpay_order_id = razorpay_order_id
        order.save()
        callback_url = "http://" + "127.0.0.1:8000" + "/razorpay/paymenthandler/"
        context = {'razorpay_order_id': razorpay_order_id, 'razorpay_merchant_key': settings.RAZORPAY_API_KEY,
                   'razorpay_amount': amount, 'currency': currency, 'callback_url': callback_url}

        return render(request, 'razorpay/payment.html', context=context)


@csrf_exempt
def paymenthandler(request):
    # only accept POST request.
    if request.method == "POST":
        payment_result = handle_payment(request)
        if payment_result == 'success':
            return render(request, 'razorpay/success.html')
        elif payment_result == 'cancelled':
            return render(request, 'razorpay/cancelled.html')
        else:
            return HttpResponseBadRequest()  # Handle other error cases
    else:
        return HttpResponseBadRequest()
