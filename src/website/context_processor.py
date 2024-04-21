from src.administration.admins.models import Cart
from src.website.utility import get_total_amount


def get_total_counts_context_processor(request):
    if request.user.is_authenticated:
        cart = Cart.objects.filter(user=request.user)
        total_amount, discount_amount, sipping_charges, sub_total = get_total_amount(request)
        return {'cart': cart, 'total_amount': total_amount, 'discounted_amount': discount_amount,
                'sipping_charges': sipping_charges, 'sub_total': sub_total}
    else:
        return {'cart': '', 'total_amount': '0', 'discounted_amount': '0',
                'sipping_charges': '0', 'sub_total': '0'}
