import razorpay
from django.contrib import messages
import stripe
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.views import View
from django.views.generic import TemplateView, ListView, DetailView

from core import settings
from src.administration.admins.models import (
    Product, Blog, BlogCategory, Order, Cart, OrderItem, ProductCategory, ProductWeight, Wishlist, ProductRating,
    TeamMember, Testimonial, Address
)
from src.website.filters import ProductFilter, BlogFilter
from src.website.forms import OrderCheckoutForm
from src.website.utility import get_total_amount, validate_product_quantity, calculate_shipment_price

""" BASIC PAGES ---------------------------------------------------------------------------------------------- """


class HomeTemplateView(TemplateView):
    template_name = 'website/home.html'

    def get_context_data(self, **kwargs):
        context = super(HomeTemplateView, self).get_context_data(**kwargs)
        context['new_products'] = Product.objects.order_by('-created_on')[:10]
        context['blogs'] = Blog.objects.order_by('-created_on')[:10]
        context['top_products'] = Product.objects.order_by('-total_views', '-total_sales', '-total_reviews')[:10]
        context['best_selling'] = Product.objects.order_by('-total_sales', )[:10]
        categories = ProductCategory.objects.all()[:10]
        context['top_categories'] = categories
        context[f'product_category_all'] = Product.objects.all()[:8]
        for i, category in enumerate(categories):
            context[f'product_category_{i}'] = Product.objects.filter(category=category)[:8]
        current_datetime = timezone.now()

        products_with_deals = Product.objects.filter(
            productdeal__started_at__lte=current_datetime,
            productdeal__expire_at__gt=current_datetime
        ).distinct()
        context['popular_discount'] = Product.objects.order_by('-discount').exclude(discount__lte=0)
        context['discount_deals'] = products_with_deals[:8]

        return context


class ProductListView(ListView):
    template_name = 'website/product_list.html'
    queryset = Product.objects.all()

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super(ProductListView, self).get_context_data(**kwargs)
        filter_product = ProductFilter(self.request.GET, queryset=self.queryset)
        pagination = Paginator(filter_product.qs, 50)
        page_number = self.request.GET.get('page')
        page_obj = pagination.get_page(page_number)
        context['object_list'] = page_obj
        context['testimonials'] = Testimonial.objects.all()
        context['filter_form'] = filter_product
        return context


class ProductDetailView(DetailView):
    template_name = 'website/product_detail.html'
    model = Product

    def get_object(self, queryset=None):
        product = get_object_or_404(Product, id=self.kwargs.get('pk'))
        product.total_views += 1
        product.save()
        return product

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super(ProductDetailView, self).get_context_data(**kwargs)
        context['related_product'] = Product.objects.filter().distinct()[:4]
        context['reviews'] = ProductRating.objects.filter(product_id=self.kwargs.get('pk'))
        return context


class BlogListView(ListView):
    model = Blog
    paginate_by = 24
    template_name = 'website/post_list.html'

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super(BlogListView, self).get_context_data(**kwargs)
        _filter = BlogFilter(self.request.GET, queryset=self.queryset)
        pagination = Paginator(_filter.qs, 20)
        page_number = self.request.GET.get('page')
        page_obj = pagination.get_page(page_number)
        context['object_list'] = page_obj
        context['filter_form'] = _filter.form
        context['recent'] = Blog.objects.order_by('-created_on')[:5]
        return context


class BlogDetailView(DetailView):
    template_name = 'website/post_detail.html'
    model = Blog

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super(BlogDetailView, self).get_context_data(**kwargs)
        post = Blog.objects.get(pk=self.kwargs['pk'])
        post.visits += 1
        post.save()
        return context


class AboutUsTemplateView(TemplateView):
    template_name = 'website/about.html'

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super(AboutUsTemplateView, self).get_context_data(**kwargs)
        context['team'] = TeamMember.objects.all()
        return context


class ContactUsTemplateView(TemplateView):
    template_name = 'website/contact_us.html'


class FranchiseTemplateView(TemplateView):
    template_name = 'website/franchise.html'


""" ORDER AND CART  ------------------------------------------------------------------------------------------ """


@method_decorator(login_required, name='dispatch')
class CartTemplateView(ListView):
    template_name = 'website/cart.html'
    model = Cart

    def get_queryset(self):
        return self.model.objects.filter(user=self.request.user)

    def get_context_data(self, **kwargs):
        context = super(CartTemplateView, self).get_context_data(**kwargs)
        context['cart'] = Cart.objects.filter(user=self.request.user)
        total_amount, discount_amount, sipping_charges, custom_sipping_charges, sub_total = get_total_amount(
            self.request)
        context['total_amount'] = total_amount
        context['discount_amount'] = discount_amount
        context['sipping_charges'] = sipping_charges
        context['sub_total'] = sub_total
        return context


@method_decorator(login_required, name='dispatch')
class AddToCart(View):
    def get(self, request, *args, **kwargs):
        product_weight_id = self.kwargs['product_weight_id']
        # check product quantity
        product = Product.objects.get(id=self.kwargs['product_id'])
        if str(product.quantity) <= "0":
            messages.error(request, 'Insufficient quantity')
            return redirect('website:product-detail', pk=self.kwargs['product_id'])

        if product_weight_id != "0":
            product_weight = ProductWeight.objects.get(id=product_weight_id)
            cart, created = Cart.objects.get_or_create(
                user=self.request.user, product_id=self.kwargs['product_id'],
                product_weight=product_weight
            )
        else:
            cart, created = Cart.objects.get_or_create(
                user=self.request.user, product_id=self.kwargs['product_id'],
            )

        if not created:
            messages.warning(request, 'Item Already in cart')
            return redirect('website:product-detail', pk=self.kwargs['product_id'])
        cart.quantity = 1
        cart.save()
        messages.success(request, 'Add to Cart Successfully')
        return redirect('website:product-detail', pk=self.kwargs['product_id'])


@method_decorator(login_required, name='dispatch')
class BuyNow(View):
    def get(self, request, *args, **kwargs):
        product_weight_id = self.kwargs['product_weight_id']
        product = Product.objects.get(id=self.kwargs['product_id'])
        if str(product.quantity) <= "0":
            messages.error(request, 'Insufficient quantity')
            return redirect('website:product-detail', pk=self.kwargs['product_id'])

        if product_weight_id != "0":
            product_weight = ProductWeight.objects.get(id=product_weight_id)
            cart, created = Cart.objects.get_or_create(
                user=self.request.user, product_id=self.kwargs['product_id'],
                product_weight=product_weight
            )
        else:
            cart, created = Cart.objects.get_or_create(
                user=self.request.user, product_id=self.kwargs['product_id'],
            )
        if created:
            cart.quantity = 1
        cart.save()
        return redirect('website:order')


@method_decorator(login_required, name='dispatch')
class UpdateCart(View):
    def get(self, request, *args, **kwargs):
        id = self.kwargs.get('id')
        quantity = int(self.kwargs.get('quantity'))
        cart = get_object_or_404(Cart, id=id, user=self.request.user)
        print(cart.product.quantity)
        if str(cart.product.quantity) <= "0":
            messages.error(request, 'Insufficient quantity')
            return redirect('website:cart')
        cart.quantity = quantity
        cart.save()
        messages.success(request, 'Cart Item Successfully Updated ')
        return redirect('website:cart')


@method_decorator(login_required, name='dispatch')
class WishListListView(ListView):
    template_name = 'website/wishlist_list.html'
    model = Wishlist

    def get_queryset(self):
        return self.model.objects.filter(user=self.request.user)


@method_decorator(login_required, name='dispatch')
class RemoveFromCartView(View):
    def get(self, request, *args, **kwargs):
        id = self.kwargs.get('pk')
        cart = get_object_or_404(Cart, id=id, user=self.request.user)
        cart.delete()
        messages.warning(request, 'Item Removed From  Cart')
        return redirect('website:cart')


@method_decorator(login_required, name='dispatch')
class AddToWishlist(View):
    def get(self, request, *args, **kwargs):
        product = self.kwargs.get('pk')
        product = get_object_or_404(Product, id=product)
        wishlist, created = Wishlist.objects.get_or_create(product=product, user=request.user)
        wishlist.save()
        if created:
            messages.success(request, 'Item Add cart Successfully ')
        messages.success(request, 'Item already in Wishlist')
        return redirect('website:wishlist_list')


@method_decorator(login_required, name='dispatch')
class DeleteFromWishlist(View):
    def get(self, request, *args, **kwargs):
        id = self.kwargs.get('pk')
        wishlist = get_object_or_404(Wishlist, id=id, user=request.user)
        wishlist.delete()
        messages.warning(request, 'Item Removed From  Wishlist')
        return redirect('website:wishlist_list')


razorpay_client = razorpay.Client(
    auth=(settings.RAZORPAY_API_KEY, settings.RAZORPAY_API_SECRET))


@method_decorator(login_required, name='dispatch')
class OrderCreate(View):
    template_name = 'website/order.html'
    cart = None
    context = {}

    def dispatch(self, request, *args, **kwargs):
        self.cart = Cart.objects.filter(user=request.user)
        if not self.cart:
            messages.error(
                request, "No items available in cart, to proceed to checkout add some items to cart first."
            )
            return redirect('website:shop')
        return super().dispatch(request, *args, **kwargs)

    def get(self, request):
        form = OrderCheckoutForm()
        currency = 'INR'
        amount = 20000
        razorpay_order = razorpay_client.order.create(dict(amount=amount,
                                                           currency=currency,
                                                           payment_capture='0'))
        razorpay_order_id = razorpay_order['id']
        callback_url = "http://" + "127.0.0.1:8000" + "/razorpay/paymenthandler/"
        payment_context = {'razorpay_order_id': razorpay_order_id, 'razorpay_merchant_key': settings.RAZORPAY_API_KEY,
                           'razorpay_amount': amount, 'currency': currency, 'callback_url': callback_url}

        address = Address.objects.filter(user=self.request.user)
        data = {
            'form': form,
            'address': address,
        }
        self.context.update(data)
        return render(request, self.template_name, self.context)

    def post(self, request):
        """
        1: check if cart is empty (in dispatch)
        2: validate form
        3: validate product quantity
        4: save the order
        5: checkout for online pay
        6: redirect to order confirmation page or any other page
        """

        # 2: VALIDATE FORM
        form = OrderCheckoutForm(request.POST)
        if form.is_valid():

            # 3: VALIDATE PRODUCT QUANTITY
            error = validate_product_quantity(request)
            if error:
                return redirect("website:order")

            # 4: SAVE THE ORDER
            order = form.save(commit=False)
            order.client = request.user
            order.save()
            return redirect('razorpay:pay', order.pk)

        messages.error(request, "There are some issues in your order, kindly review your order once again.")
        return render(request, self.template_name, {'form': form})


@method_decorator(login_required, name='dispatch')
class ShipmentPriceRetrieveView(View):
    def get(self, *args, **kwargs):
        shipment_charges = "Select Shipment Type and Service Type"
        service_type = self.request.POST.get('service_type')
        shipment_type = self.request.POST.get('shipment_type')
        state = self.request.POST.get('state')
        if state and shipment_type and service_type:
            shipment_charges = calculate_shipment_price(self.request, service_type, state, shipment_type)
        context = {'shipment_charges': shipment_charges}
        return render(self.request, template_name='website/htmx/shipment_charges.html', context=context)


@method_decorator(login_required, name='dispatch')
class SuccessPayment(View):
    def get(self, request, *args, **kwargs):
        stripe_id = self.request.GET.get('session_id')
        order = get_object_or_404(Order, user=self.request.user, stripe_payment_id=stripe_id)
        order.paid = order.total
        order.payment_status = 'completed'
        order.order_status = 'shipping'
        order.save()
        cart = Cart.objects.filter(user=self.request.user)
        for cart in cart:
            cart_item = OrderItem(product=cart.product, order=order,
                                  qty=cart.quantity)
            cart_item.save()
            cart.delete()
        return render(self.request, 'website/success.html')


@method_decorator(login_required, name='dispatch')
class CancelPayment(View):
    template_name = 'website/cancel.html'

    def get(self, *args):
        stripe_id = self.request.GET.get('session_id')
        order = Order.objects.get(user=self.request.user, stripe_payment_id=stripe_id)
        order.delete()
        return render(self.request, template_name=self.template_name)


"""----------------------------ISSUES PAGES ------------------------------------------------------------------- """


class CookiePolicy(TemplateView):
    template_name = 'website/cookie_policy.html'


class PrivacyPolicy(TemplateView):
    template_name = 'website/privacy_policy.html'


class TermsAndCondition(TemplateView):
    template_name = 'website/terms_and_conditions.html'


class Jobs(TemplateView):
    template_name = 'website/jobs.html'


class ReturnPolicy(TemplateView):
    template_name = 'website/return_policy.html'


class ShippingPolicy(TemplateView):
    template_name = 'website/shipping_policy.html'
