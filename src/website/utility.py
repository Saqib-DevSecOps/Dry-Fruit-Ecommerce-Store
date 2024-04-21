from src.administration.admins.models import Cart


def session_id(self):
    session_key = self.request.session.session_key
    if not session_key:
        session_key = self.request.session.create()
    return session_key


def get_total_amount(request):
    cart = Cart.objects.filter(user=request.user)
    total_price = 0
    discount_price = 0
    for cart in cart:
        total_price += float(cart.get_item_price())
        discount_price += float(cart.get_discount_price())

    shipping_charges = discount_price * 0.05
    sub_total = discount_price + shipping_charges
    return total_price, discount_price , shipping_charges , sub_total


def total_quantity(request):
    cart = Cart.objects.filter(user=request.user)
    quantity = 0
    for cart in cart:
        quantity += cart.quantity
    return quantity
