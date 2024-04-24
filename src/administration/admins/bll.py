from django.contrib import messages
from core.bll import calculate_shipping_charges, calculate_service_charges
from src.administration.admins.models import OrderItem, Cart

""" HELPERS """


# VERIFIED
def validate_product_quantity(request):
    error_message = False
    cart_item = Cart.objects.filter(user=request.user)
    for _cart_item in cart_item:
        if _cart_item.quantity > _cart_item.product.quantity:
            error_message = True
            messages.error(request, f"Insufficient quantity of {_cart_item.product.title} "
                                    f"in stock , Available Quantity is {_cart_item.product.quantity}")
    if error_message:
        return error_message


# VERIFIED
def order_repay_quantity_check(request, order):
    error_message = False
    order_item = OrderItem.objects.filter(order=order)
    for _order_item in order_item:
        if _order_item.product.quantity < _order_item.quantity:
            error_message = True
            messages.error(request, f"Insufficient quantity of {_order_item.product.title} "
                                    f"in stock , Available Quantity is {_order_item.product.quantity}")
    if error_message:
        return error_message
    return error_message


""" ORDERS """


def get_cart_calculations(user):
    cart = Cart.objects.filter(user=user)
    total_price = 0
    discount_price = 0
    for cart in cart:
        total_price += float(cart.get_item_price())
        discount_price += float(cart.get_discount_price())

    shipping_charges = calculate_shipping_charges(discount_price)
    service_charges = calculate_service_charges(discount_price)
    sub_total = discount_price + shipping_charges + service_charges
    return total_price, service_charges, shipping_charges, sub_total


# VERIFIED
def create_order_items(order, user_request):
    """
    1: Calculate Charge
    1: Create Order Items
    3: Delete Cart Items
    4: Update Order
    """

    # 1: Calculate Charge
    cart = Cart.objects.filter(user=user_request)
    total, service_charges, shipping_charges, sub_total = get_cart_calculations(user_request)
    # 2: Create Order Items
    order_items = [
        OrderItem(order=order, product=cart_item.product, qty=cart_item.quantity) for cart_item in cart
    ]
    OrderItem.objects.bulk_create(order_items)

    # 3: Delete Cart Items
    cart.delete()

    # 4: Update Order
    order.total = total
    order.sub_total = sub_total
    order.service_charges = service_charges

    # order.shipping_charges = shipping_charges
    order.save()
    return order
