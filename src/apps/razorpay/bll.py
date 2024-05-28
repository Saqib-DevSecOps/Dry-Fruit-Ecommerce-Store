import razorpay
from django.shortcuts import get_object_or_404

from core.settings import RAZORPAY_API_KEY, RAZORPAY_API_SECRET, BASE_URL
from src.administration.admins.models import Order, OrderItem, Payment

razorpay_client = razorpay.Client(
    auth=(RAZORPAY_API_KEY, RAZORPAY_API_SECRET))


def payment_success(payment_id, razorpay_order_id):
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
                return 'success', order
            except Exception as e:
                print(f"Internal error while processing the order: {e}")
                return 'cancelled', None
        else:
            print("Payment verification failed.")
            return 'cancelled', None
    except Exception as e:
        print(f"Error in payment handling: {e}")
        return 'error', None


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
