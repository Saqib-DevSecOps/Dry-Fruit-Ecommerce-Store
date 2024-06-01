import re
from datetime import datetime, timedelta

from _decimal import Decimal
from django.contrib import messages
from django.db.models import Sum

from core.bll import calculate_shipping_charges, calculate_service_charges
from src.administration.admins.models import OrderItem, Cart, Payment, Order
from src.website.utility import calculate_volumetric_weight, get_chargeable_weight, calculate_shipping_cost

""" HELPERS """


def get_sales_by_month():
    current_year = datetime.now().year
    sales_by_month = []
    for month in range(1, 13):
        start_date = datetime(current_year, month, 1)
        end_date = start_date.replace(day=1, month=month % 12 + 1, year=start_date.year + month // 12) - timedelta(
            days=1)
        total_sales = Order.objects.filter(
            created_on__date__gte=start_date,
            created_on__date__lte=end_date
        ).aggregate(total=Sum('total'))['total']
        sales_by_month.append(total_sales or 0)
    return sales_by_month


def get_orders_by_month():
    current_year = datetime.now().year
    orders = Order.objects.filter(created_on__year=current_year)
    order_counts = [0] * 12
    for order in orders:
        month = order.created_on.month
        order_counts[month - 1] += 1
    return order_counts


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


def match_state(state_patterns, state):
    state = state.lower()
    for key, pattern in state_patterns.items():
        if re.search(pattern, state):
            return key
    return "other"


def calculate_custom_shipping_cost(chargeable_weight, service_type, matched_state):
    if service_type == "normal":
        if matched_state == "gujarat":
            return 30 * chargeable_weight
        elif matched_state == "mumbai":
            return 60 * chargeable_weight
        else:
            return 80 * chargeable_weight
    elif service_type == "fast":
        if chargeable_weight <= 0.5:
            if matched_state == "gujarat":
                return 150
            elif matched_state == "mumbai":
                return 250
            else:
                return 300
        elif chargeable_weight <= 1:
            if matched_state == "gujarat":
                return 200
            elif matched_state == "mumbai":
                return 300
            else:
                return 350

        else:
            if matched_state == "gujarat":
                return 200 * chargeable_weight
            elif matched_state == "mumbai":
                return 300 * chargeable_weight
            else:
                return 350 * chargeable_weight
    else:
        return 1


def get_custom_shipping_charge(cart_items, service_type, state):
    custom_shipping_cost = Decimal(0)
    state_patterns = {
        "gujarat": r"gujarat",
        "mumbai": r"mumbai",
        "other": r"other"
    }
    matched_state = match_state(state_patterns, state)

    for cart_item in cart_items:
        if cart_item.product_weight is not None:
            actual_weight = cart_item.product_weight.get_product_size()
        else:
            actual_weight = 0
        custom_shipping_cost += calculate_custom_shipping_cost(actual_weight.weight, service_type, matched_state)
    return custom_shipping_cost


def get_cart_calculations(user):
    cart_items = Cart.objects.filter(user=user)
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


def calculate_tax(item):
    pass


# VERIFIED
def create_order_items(order, user_request):
    """
    1: Calculate Charge
    1: Create Order Items
    3: Delete Cart Items
    4: Update Order
    """
    tax = Decimal(0)
    # 1: Calculate Charge
    cart = Cart.objects.filter(user=user_request)
    total, service_charges, shipping_charges, sub_total = get_cart_calculations(user_request)
    custom_shipping_cost = get_custom_shipping_charge(cart, order.service_type, order.state)

    # 2: Create Order Items
    order_items = [
        OrderItem(order=order, product=cart_item.product, product_weight=cart_item.product_weight,
                  qty=cart_item.quantity) for cart_item in cart
    ]
    OrderItem.objects.bulk_create(order_items)

    order_items = OrderItem.objects.filter(order=order)
    tax += sum(item.get_tax() for item in order_items)
    cart.delete()

    # 4: Update Order
    if order.shipment_type == "custom":
        sub_total = sub_total - shipping_charges
        sub_total = sub_total + custom_shipping_cost
        final_shipping_charges = custom_shipping_cost
    else:
        final_shipping_charges = shipping_charges

    order.total = total
    order.sub_total = int(sub_total) + int(tax)
    order.service_charges = service_charges
    order.shipping_charges = final_shipping_charges
    order.tax = tax
    order.save()
    payment, created = Payment.objects.get_or_create(order=order)
    payment.save()
    return order
