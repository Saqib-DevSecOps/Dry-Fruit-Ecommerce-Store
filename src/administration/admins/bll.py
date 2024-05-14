from datetime import datetime, timedelta

from django.contrib import messages
from django.db.models import Sum

from core.bll import calculate_shipping_charges, calculate_service_charges
from src.administration.admins.models import OrderItem, Cart, Payment, Order

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
        OrderItem(order=order, product=cart_item.product, product_weight=cart_item.product_weight,
                  qty=cart_item.quantity) for cart_item in cart
    ]
    OrderItem.objects.bulk_create(order_items)

    # 3: Delete Cart Items
    cart.delete()

    # 4: Update Order
    order.total = total
    order.sub_total = int(sub_total)
    order.service_charges = service_charges
    order.shipping_charges = shipping_charges
    order.save()
    payment, created = Payment.objects.get_or_create(order=order)
    payment.save()
    return order
