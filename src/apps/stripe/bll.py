import stripe
from django.shortcuts import redirect, get_object_or_404
from django.urls import reverse
from src.administration.admins.models import OrderItem, Order
from src.website.utility import validate_product_quantity
from core.settings import BASE_URL

"""Stripe CheckOut"""


def stripe_checkout_create(request, order, host):
    error = validate_product_quantity(request)
    if error:
        return redirect("website:checkout")

    session = stripe.checkout.Session.create(
        payment_method_types=['card'],
        line_items=[{
            'price_data': {
                'currency': 'usd',
                'product_data': {
                    'name': f'Order ID# {order.pk}',
                },
                'unit_amount': int(order.total * 100),
            },
            'quantity': 1,
        }],
        mode='payment',
        success_url=BASE_URL + reverse('stripe:success') + '?session_id={CHECKOUT_SESSION_ID}',
        cancel_url=BASE_URL + reverse('stripe:cancel') + '?session_id={CHECKOUT_SESSION_ID}',
    )

    order.stripe_id = session['id']
    order.save()

    # # Create a payment object
    # payment = Payment.objects.create(
    #     order=order,
    #     variant='Stripe',
    #     transaction_id=session['id'],
    #     description=f'Payment for Order ID# {order.pk}',
    #     currency='usd',
    #     total=order.total,
    #     status=PaymentStatus.INPUT,
    # )

    return session


def checkout_payment_success(stripe_id, order):
    order.payment_status = 'paid'
    order.order_status = 'approved'
    order.save()

    # payment = get_object_or_404(Payment, transaction_id=stripe_id)
    # payment.status = PaymentStatus.CONFIRMED
    # payment.save()

    order_items = OrderItem.objects.filter(order=order)
    for order_item in order_items:
        if order_item.product.quantity >= order_item.qty:
            product = order_item.product
            ordered_quantity = order_item.qty
            product.quantity -= ordered_quantity
            product.save()
    # Send Email Message to Buyer
    # send_email_message(buyer_order_placed_subject, order, TEMPLATE_BUYER_ORDER_PLACED)
    # for _order in sub_orders:
    #     Send Email Message to Vendor(s)
    # send_email_message(vendor_order_placed_subject, _order, TEMPLATE_VENDOR_ORDER_PLACED)


def checkout_payment_failed(stripe_id):
    order = get_object_or_404(Order, stripe_id=stripe_id)
    order.stripe_id = None
    # payment = get_object_or_404(Payment, transaction_id=stripe_id)
    # payment.delete()
    order.save()
