import base64
import io
from django.contrib import messages

import stripe
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import OuterRef, Subquery, Q
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.views import View
from django.views.generic import TemplateView, ListView, DetailView

from src.administration.admins.models import (
    Product, Blog, BlogCategory, Order, Cart, OrderItem, ProductCategory, ProductWeight, Wishlist
)
from src.apps.stripe.views import create_stripe_checkout_session
from src.website.filters import ProductFilter, BlogFilter
from src.website.forms import OrderCheckoutForm
from src.website.utility import get_total_amount, validate_product_quantity

""" BASIC PAGES ---------------------------------------------------------------------------------------------- """


class HomeTemplateView(TemplateView):
    template_name = 'website/home.html'

    def get_context_data(self, **kwargs):
        context = super(HomeTemplateView, self).get_context_data(**kwargs)
        context['new_products'] = Product.objects.order_by('-created_on')[:10]
        context['blogs'] = Blog.objects.order_by('-created_on')[:10]
        context['top_products'] = Product.objects.order_by('-total_views', '-total_sales', '-total_reviews')[:5]
        categories = ProductCategory.objects.all()[:5]
        context['top_categories'] = categories
        context[f'product_category_all'] = Product.objects.all()[:8]
        for i, category in enumerate(categories):
            context[f'product_category_{i}'] = Product.objects.filter(category=category)[:8]
        context['popular_discount'] = Product.objects.order_by('-discount')[:8]

        return context


class ContactUsTemplateView(TemplateView):
    template_name = 'website/contact_us.html'


class AboutUsTemplateView(TemplateView):
    template_name = 'website/about.html'


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
        context['filter_form'] = filter_product
        return context


class ProductDetailView(DetailView):
    template_name = 'website/product_detail.html'
    model = Product

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super(ProductDetailView, self).get_context_data(**kwargs)
        product = Product.objects.get(pk=self.kwargs['pk'])
        context['related_product'] = Product.objects.filter().distinct()[:4]
        return context


class BlogListView(ListView):
    model = Blog
    paginate_by = 24
    template_name = 'website/post_list.html'

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super(BlogListView, self).get_context_data(**kwargs)
        category = self.request.GET.get('category')

        if category and self.request is not None:
            post = Blog.objects.filter(category__id=category)
        else:
            post = Blog.objects.all().order_by('-created_on')
        context['recent'] = Blog.objects.order_by('-created_on')[:5]
        context['popular_posts'] = Blog.objects.order_by('-visits', '-read_time')[:5]
        filter_posts = BlogFilter(self.request.GET, queryset=post)
        pagination = Paginator(filter_posts.qs, 24)
        page_number = self.request.GET.get('page')
        page_obj = pagination.get_page(page_number)
        context['post_category'] = BlogCategory.objects.all()
        context['posts'] = page_obj
        context['filter_form'] = filter_posts
        context['category'] = category
        return context


class BlogDetailView(TemplateView):
    template_name = 'website/post_detail.html'
    # model = Blog
    # pk_url_kwarg = "post_id"
    # slug_url_kwarg = 'slug'
    # query_pk_and_slug = True
    #
    # def get_context_data(self, *, object_list=None, **kwargs):
    #     context = super(BlogDetailView, self).get_context_data(**kwargs)
    #     post = Blog.objects.get(slug=self.kwargs['slug'])
    #     post.visits += 1
    #     post.save()
    #     return context


""" ORDER AND CART  ------------------------------------------------------------------------------------------ """


# @method_decorator(login_required, name='dispatch')
class CartTemplateView(ListView):
    template_name = 'website/cart.html'
    model = Cart

    def get_context_data(self, **kwargs):
        context = super(CartTemplateView, self).get_context_data(**kwargs)
        context['cart'] = Cart.objects.filter(user=self.request.user)
        total_amount, discount_amount, sipping_charges, sub_total = get_total_amount(self.request)
        context['total_amount'] = total_amount
        context['discount_amount'] = discount_amount
        context['sipping_charges'] = sipping_charges
        context['sub_total'] = sub_total
        return context


@method_decorator(login_required, name='dispatch')
class AddToCart(View):
    def get(self, request, *args, **kwargs):
        product_weight_id = self.kwargs['product_weight_id']
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
class UpdateCart(View):
    def get(self, request, *args, **kwargs):
        id = self.kwargs.get('id')
        quantity = int(self.kwargs.get('quantity'))
        cart = get_object_or_404(Cart, id=id, )
        cart.quantity += quantity
        cart.save()
        messages.success(request, 'Cart Item Successfully Updated ')
        return redirect('website:cart')


class WishListListView(ListView):
    template_name = 'website/wishlist_list.html'
    model = Wishlist


@method_decorator(login_required, name='dispatch')
class RemoveFromCartView(View):
    def get(self, request, *args, **kwargs):
        id = self.kwargs.get('pk')
        cart = get_object_or_404(Cart, id=id, user=self.request.user)
        cart.delete()
        messages.warning(request, 'Item Removed From  Cart')
        return redirect('website:cart')


# @method_decorator(login_required, name='dispatch')
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


# @method_decorator(login_required, name='dispatch')
class DeleteFromWishlist(View):
    def get(self, request, *args, **kwargs):
        id = self.kwargs.get('pk')
        wishlist = get_object_or_404(Wishlist, id=id, user=request.user)
        wishlist.delete()
        messages.warning(request, 'Item Removed From  Wishlist')
        return redirect('website:wishlist_list')


stripe.api_key = 'sk_test_51MzSVMKxiugCOnUxT0YN5E7M8BhbZrzPFrx6NE6vRwmkTIYKREvGTyLBfXhbdORJybRfmzVm2cjPBTkkuGyAjVfP00cf3sDcP9'


# @method_decorator(login_required, name='dispatch')


@method_decorator(login_required, name='dispatch')
class OrderCreate(View):
    template_name = 'website/order.html'
    cart = None
    total = 0
    service_charges = 0
    shipping_charges = 0
    sub_total = 0

    def dispatch(self, request, *args, **kwargs):
        self.cart = Cart.objects.filter(user=request.user)
        self.total, self.service_charges, self.shipping_charges, self.sub_total = get_total_amount(self.request)

        # 1: CHECK IF THE CART IS EMPTY
        if not self.cart:
            messages.error(
                request, "No items available in cart, to proceed to checkout add some items to cart first."
            )
            return redirect('website:shop')

        return super().dispatch(request, *args, **kwargs)

    def get(self, request):
        form = OrderCheckoutForm()
        context = {
            'form': form,
            'user_cart': self.cart,
            'total': self.total,
            'service_charges': self.service_charges,
            'shipping_charges': self.shipping_charges,
            'sub_total': self.sub_total,
        }
        return render(request, self.template_name, context)

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

            # 5: CHECKOUT FOR ONLINE PAY
            if order.is_online():
                session_url = create_stripe_checkout_session(request, order)
                return redirect(session_url)

            # 6: REDIRECT TO ORDER CONFIRMATION PAGE OR ANY OTHER PAGE
            messages.success(request, "Your order placed successfully")
            return redirect('website:order_detail', order.pk)

        messages.error(request, "There are some issues in your order, kindly review your order once again.")
        context = {
            'form': form,
            'user_cart': self.cart,
            'total': self.total,
            'service_charges': self.service_charges,
            'shipping_charges': self.shipping_charges,
            'sub_total': self.sub_total,
        }
        return render(request, self.template_name, context)

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
