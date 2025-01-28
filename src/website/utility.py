import re

from _decimal import Decimal
from django.contrib import messages
from django.utils import timezone

from src.administration.admins.models import Cart, Coupon, BuyerCoupon, Package


def session_id(self):
    session_key = self.request.session.session_key
    if not session_key:
        session_key = self.request.session.create()
    return session_key


def calculate_volumetric_weight(length, width, height, divisor=Decimal('5000')):
    packages = Package.objects.all()
    cart_volume = length * width * height
    cart_volume *= Decimal('1.10')
    actual_weight = cart_volume
    for package in packages:
        if int(package.get_total_dimensions()) == int(cart_volume + Decimal('0.5')):
            actual_weight = package.get_total_dimensions()
            break
    return actual_weight / divisor


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


def get_total_amount(user):
    cart_items = Cart.objects.filter(user=user)

    discount_amount = Decimal(0)
    sub_total = Decimal(0)
    total_price = Decimal(0)
    coupon_discount = Decimal(0)
    discount_price = Decimal(0)
    shiprocket_shipping_charges = Decimal(0)
    custom_shipping_charges = Decimal(0)
    base_rate = Decimal('26')
    additional_500g_rate = Decimal('15')

    for cart_item in cart_items:
        product_size = cart_item.get_product_size()
        quantity = cart_item.quantity  # Fetch the quantity of the item in the cart

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

        # Add 10% to dimensions
        length += length * Decimal('0.10')
        width += width * Decimal('0.10')
        height += height * Decimal('0.10')

        total_price += Decimal(cart_item.get_item_price())
        sub_total += Decimal(cart_item.get_discount_price())
        discount_price += Decimal(cart_item.get_item_price()) - Decimal(cart_item.get_discount_price())
        volumetric_weight = calculate_volumetric_weight(length, width, height)
        chargeable_weight = get_chargeable_weight(weight, volumetric_weight)

        item_shipping_charges = calculate_shipping_cost(chargeable_weight, base_rate, additional_500g_rate)
        shiprocket_shipping_charges += item_shipping_charges * quantity

        # Apply all unused coupons discounts
        buyer_coupons = BuyerCoupon.objects.filter(user=user, is_used=False)
        for buyer_coupon in buyer_coupons:
            coupon = buyer_coupon.coupon
            if coupon.is_active and coupon.valid_from <= timezone.now() <= coupon.valid_to:
                discount_amount = sub_total * (coupon.discount / Decimal('100'))
                buyer_coupon.save()

    coupon_discount = discount_amount
    sub_total = sub_total - coupon_discount
    return total_price, discount_price, shiprocket_shipping_charges, custom_shipping_charges, sub_total, coupon_discount


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


def match_state(state_patterns, state):
    state = state.lower()
    for key, pattern in state_patterns.items():
        if re.search(pattern, state):
            return key
    return "other"


def calculate_custom_shipping_cost(chargeable_weight, service_type, matched_state):
    chargeable_weight = int(chargeable_weight + 0.5)
    if service_type == "normal":
        if matched_state == "local":
            return 30 * chargeable_weight
        elif matched_state == "gujarat":
            return 40 * chargeable_weight
        elif matched_state == "mumbai":
            return 60 * chargeable_weight
        else:
            return 80 * chargeable_weight
    elif service_type == "fast":
        if chargeable_weight <= 0.5:
            if matched_state == "local":
                return 150
            elif matched_state == "gujarat":
                return 200
            elif matched_state == "mumbai":
                return 250
            else:
                return 300
        elif chargeable_weight <= 1:
            if matched_state == "local":
                return 200
            elif matched_state == "gujarat":
                return 250
            elif matched_state == "mumbai":
                return 300
            else:
                return 350

        else:
            if matched_state == "local":
                return 200 * chargeable_weight
            elif matched_state == "gujarat":
                return 250 * chargeable_weight
            elif matched_state == "mumbai":
                return 300 * chargeable_weight
            else:
                return 350 * chargeable_weight
    else:
        return 1


def get_custom_shipping_charge(request, service_type, state):
    custom_shipping_cost = Decimal(0)
    cart_items = Cart.objects.filter(user=request.user)
    state_patterns = {
        "local": r"local",
        "gujarat": r"gujarat",
        "mumbai": r"mumbai",
        "other": r"other"
    }
    matched_state = match_state(state_patterns, state)

    for cart_item in cart_items:
        product_size = cart_item.get_product_size()
        quantity = cart_item.quantity  # Fetch the quantity of the item in the cart

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

        volumetric_weight = calculate_volumetric_weight(length, width, height)
        chargeable_weight = get_chargeable_weight(weight, volumetric_weight)
        item_shipping_cost = calculate_custom_shipping_cost(chargeable_weight, service_type, matched_state)
        custom_shipping_cost += item_shipping_cost * quantity

    return custom_shipping_cost


def calculate_shipment_price(request, service_type, state, shipment_type):
    if shipment_type == "custom_shipment":
        custom_shipping_cost = get_custom_shipping_charge(request, service_type, state)
        return custom_shipping_cost
    total_price, discount_price, shiprocket_shipping_charges, custom_shipping_charges, sub_total, coupon_discount = get_total_amount(
        request.user)
    return shiprocket_shipping_charges
