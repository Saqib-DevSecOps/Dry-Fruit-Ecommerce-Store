from _decimal import Decimal
from django.contrib import messages

from src.administration.admins.models import Cart


def session_id(self):
    session_key = self.request.session.session_key
    if not session_key:
        session_key = self.request.session.create()
    return session_key


def calculate_volumetric_weight(length, width, height, divisor=Decimal('5000')):
    return (length * width * height) / divisor


def get_chargeable_weight(actual_weight, volumetric_weight):
    return max(actual_weight, volumetric_weight)


def calculate_shipping_cost(chargeable_weight, base_rate, additional_500g_rate):
    if chargeable_weight <= Decimal('0.5'):
        return base_rate
    else:
        cost = base_rate
        remaining_weight = chargeable_weight - Decimal('0.5')
        additional_cost = (remaining_weight // Decimal('0.5')) * additional_500g_rate
        if remaining_weight % Decimal('0.5') != 0:
            additional_cost += additional_500g_rate
        cost += additional_cost
        return cost


def get_total_amount(request):
    cart_items = Cart.objects.filter(user=request.user)

    total_price = Decimal(0)
    discount_price = Decimal(0)
    shipping_charges = Decimal(0)
    base_rate = Decimal('26')
    additional_500g_rate = Decimal('15')

    for cart_item in cart_items:
        product_size = cart_item.get_product_size()
        if product_size:
            length = Decimal(product_size.length)
            width = Decimal(product_size.breadth)
            height = Decimal(product_size.height)
            weight = Decimal(product_size.weight)
        else:
            length = Decimal('10')
            width = Decimal('10')
            height = Decimal('10')
            weight = Decimal('1')

        total_price += Decimal(cart_item.get_discount_price())
        discount_price += Decimal(cart_item.get_item_price()) - Decimal(cart_item.get_discount_price())
        volumetric_weight = calculate_volumetric_weight(length, width, height)
        chargeable_weight = get_chargeable_weight(weight, volumetric_weight)
        shipping_charges += calculate_shipping_cost(chargeable_weight, base_rate, additional_500g_rate)

    sub_total = total_price + shipping_charges
    return total_price, discount_price, shipping_charges, sub_total


def total_quantity(request):
    cart = Cart.objects.filter(user=request.user)
    quantity = 0
    for cart in cart:
        quantity += cart.quantity
    return quantity


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
