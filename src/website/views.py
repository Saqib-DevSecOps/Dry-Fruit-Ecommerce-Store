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
    Product, Blog, BlogCategory, Order, Cart, OrderItem, ProductCategory, ProductWeight, Wishlist, BuyerAddress
)
from src.website.filters import ProductFilter, BlogFilter
from src.website.forms import OrderForm
from src.website.utility import get_total_amount

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
class OrderCreate(View):

    def get(self, request):
        cart = Cart.objects.filter(user=self.request.user)
        buyer_address = BuyerAddress.objects.filter(user=self.request.user)
        total_amount, discount_amount, sipping_charges, sub_total = get_total_amount(self.request)
        context = {'cart': cart, 'sub_total': sub_total, 'shipping_charges': sipping_charges,
                   'buyer_address': buyer_address, 'order_form': OrderForm}
        return render(request, 'website/order.html', context)

    # def post(self, request):
    #     form = OrderForm(request.POST)
    #     if form.is_valid():
    #         shipping = self.request.POST.get('shipping')
    #         if shipping == "normal":
    #             shipping_charges = 6
    #         else:
    #             shipping_charges = 10
    #         price = int(total_amount(request)) + shipping_charges
    #         line_items = []
    #         cart = Cart.objects.filter(user=self.request.user)
    #         qty = 0
    #         for product in cart:
    #             line_items.append({
    #                 'price_data': {
    #                     'currency': 'usd',
    #                     'unit_amount': int(product.product.price * 100),
    #                     'product_data': {
    #                         'name': product.product.name,
    #                     },
    #                 },
    #                 "quantity": product.quantity
    #             })
    #         for shipping in cart:
    #             line_items.append({
    #                 'price_data': {
    #                     'currency': 'usd',
    #                     'unit_amount': int(shipping_charges * 100),
    #                     'product_data': {
    #                         'name': 'Tax'
    #                     },
    #                 },
    #                 "quantity": '1'
    #             })
    #             break
    #         host = self.request.get_host()
    #         customer = stripe.Customer.create(
    #             name=self.request.user.username,
    #             email=self.request.user.email
    #         )
    #         checkout_session = stripe.checkout.Session.create(
    #             payment_method_types=['card'],
    #             customer=customer,
    #             submit_type='pay',
    #             line_items=line_items,
    #             mode='payment',
    #             success_url='http://' + host + reverse('website:success') \
    #                         + '?session_id={CHECKOUT_SESSION_ID}',
    #             cancel_url='http://' + host + reverse('website:cancel') \
    #                        + '?session_id={CHECKOUT_SESSION_ID}',
    #
    #         )
    #         stripe_id = checkout_session['id']
    #         order = form.save(commit=False)
    #         order.user = self.request.user
    #         order.total = total_amount(request)
    #         order.stripe_payment_id = stripe_id
    #         if shipping == "normal":
    #             order.shipping = "Normal"
    #         elif shipping == "premium":
    #             order.shipping = "Premium"
    #         else:
    #             pass
    #         order.save()
    #         cart = Cart.objects.filter(user=self.request.user)
    #         for cart in cart:
    #             cart_item = OrderItem(product=cart.product, order=order,
    #                                   qty=cart.quantity)
    #             cart_item.save()
    #         return redirect(checkout_session.url, code=303)
    #     else:
    #         form = OrderForm()
    #     return render(request, 'website/order.html', context={'form': OrderForm()})


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
