import razorpay
from django.shortcuts import get_object_or_404

from core.settings import RAZORPAY_API_KEY, RAZORPAY_API_SECRET
from src.administration.admins.models import Order, OrderItem, Payment

razorpay_client = razorpay.Client(
    auth=(RAZORPAY_API_KEY, RAZORPAY_API_SECRET))



def payment_success(payment_id,razorpay_order_id):
    order = get_object_or_404(Order, razorpay_order_id=razorpay_order_id)
    order.payment_status = 'paid'
    order.order_status = 'approved'
    order_items = OrderItem.objects.filter(order=order)
    for order_item in order_items:
        if order_item.product.quantity >= order_item.qty:
            product = order_item.product
            ordered_quantity = order_item.qty
            product.quantity -= ordered_quantity
            product.save()
    order.save()
    payment = get_object_or_404(Payment, order=order)
    payment.razorpay_payment_id = payment_id
    payment.razorpay_order_id = razorpay_order_id
    payment.payment_status = "completed"
    payment.amount_paid = order.sub_total
    payment.save()

def create_razorpay_checkout_session(order):
    currency = 'INR'
    amount = 20000
    razorpay_order = razorpay_client.order.create(dict(amount=amount,
                                                       currency=currency,
                                                       payment_capture='0'))
    razorpay_order_id = razorpay_order['id']
    callback_url = "http://" + "127.0.0.1:8000" + "/razorpay/paymenthandler/"
    context = {'razorpay_order_id': razorpay_order_id, 'razorpay_merchant_key': RAZORPAY_API_KEY,
               'razorpay_amount': amount, 'currency': currency, 'callback_url': callback_url}
    return context


def handle_payment(request):
    try:
        payment_id = request.POST.get('razorpay_payment_id', '')
        razorpay_order_id = request.POST.get('razorpay_order_id', '')
        signature = request.POST.get('razorpay_signature', '')
        params_dict = {
            'razorpay_order_id': razorpay_order_id,
            'razorpay_payment_id': payment_id,
            'razorpay_signature': signature
        }

        result = razorpay_client.utility.verify_payment_signature(params_dict)
        if result is not None:
            try:
                order = get_object_or_404(Order, razorpay_order_id=razorpay_order_id)
                order.payment_status = 'paid'
                order.order_status = 'approved'
                order_items = OrderItem.objects.filter(order=order)
                for order_item in order_items:
                    if order_item.product.quantity >= order_item.qty:
                        product = order_item.product
                        ordered_quantity = order_item.qty
                        product.quantity -= ordered_quantity
                        product.save()
                order.save()
                payment = get_object_or_404(Payment, order=order)
                payment.razorpay_payment_id = payment_id
                payment.razorpay_order_id = razorpay_order_id
                payment.razorpay_signature_id = signature
                payment.payment_status = "completed"
                payment.amount_paid = order.sub_total
                payment.save()
                return 'success'  # Indicate successful payment
            except:
                return 'cancelled'  # Indicate payment capture failure
        else:
            return 'cancelled'  # Indicate signature verification failure
    except:
        return 'error'  # Indicate error in processing the payment


def get_razorpay_order_id(self, request, order_id):
    currency = 'INR'
    order = get_object_or_404(Order, id=order_id)
    amount = int(order.sub_total)
    razorpay_order = razorpay_client.order.create(dict(amount=amount,
                                                       currency=currency,
                                                       payment_capture='0'))
    razorpay_order_id = razorpay_order['id']
    order.razorpay_order_id = razorpay_order_id
    order.save()
    return razorpay_order_id
