from django.contrib import messages
from django.shortcuts import render, get_object_or_404, redirect
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

        order_id = self.kwargs.get('pk')
        order = Order.objects.get(id=order_id)
        print("Debugging 1")
        amount = int(order.sub_total*100)
        print(amount)
        if order.payment_status == "paid":
            messages.error(request, "Already Paid For this Order")
            return redirect("client:order_detail", pk=order_id)

        if amount < 1:
            messages.error(request, "Amount Should be at least 1 INR")
            return redirect("client:order_detail", pk=order_id)

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
