from src.administration.admins.models import Cart


def session_id(self):
    session_key = self.request.session.session_key
    if not session_key:
        session_key = self.request.session.create()
    return session_key


def total_amount(request):
    cart = Cart.objects.filter(user=request.user)
    total_price = 0
    for cart in cart:
        total_price += float(cart.get_item_price())
    return total_price


def total_quantity(request):
    cart = Cart.objects.filter(user=request.user)
    quantity = 0
    for cart in cart:
        quantity += cart.quantity
    return quantity

