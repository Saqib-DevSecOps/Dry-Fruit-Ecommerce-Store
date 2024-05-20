import json
from allauth.account.views import PasswordSetView, PasswordChangeView
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q, OuterRef, Subquery
from django.shortcuts import redirect
from django.urls import reverse, reverse_lazy
from django.utils.decorators import method_decorator
from django.views import View
from django.views.generic import TemplateView, UpdateView, ListView, DetailView, CreateView
from src.accounts.decorators import client_protected
from src.accounts.models import Address
from src.administration.admins.models import Wishlist, Order, Product, OrderItem, Payment, Shipment, ShipRocketOrder, \
    ProductRating
from src.administration.client.bll import calculate_reviews
from src.administration.client.forms import AddressForm, UserProfileForm

from django.shortcuts import get_object_or_404, render

from src.apps.shipment.bll import track_shipping


# Create your views here.
@method_decorator(client_protected, name='dispatch')
class UserUpdateView(View):

    def get(self, request):
        form = UserProfileForm(instance=request.user)
        context = {'form': form}
        return render(request, template_name='client/user_update_form.html', context=context)

    def post(self, request):
        form = UserProfileForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            messages.success(request, "Your profile updated successfully")
            form.save(commit=True)
            return redirect('client:dashboard')
        context = {'form': form}
        return render(request, template_name='client/user_update_form.html', context=context)


@method_decorator(client_protected, name='dispatch')
class AddressUpdate(UpdateView):
    form_class = AddressForm
    model = Address
    template_name = 'client/address_form.html'

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super(AddressUpdate, self).form_valid(form)

    def get_success_url(self):
        return reverse('client:dashboard')


@method_decorator(client_protected, name='dispatch')
class ClientDashboard(TemplateView):
    template_name = 'client/client_dashboard.html'

    def get_context_data(self, **kwargs):
        context = super(ClientDashboard, self).get_context_data(**kwargs)
        context['total_orders'] = Order.objects.filter(client=self.request.user).count()
        context['pending_orders'] = Order.objects.filter(client=self.request.user, order_status="pending").count()
        context['completed_orders'] = Order.objects.filter(client=self.request.user, order_status="completed").count()
        return context


def get_paginated_context_data(self, queryset, page_size=5):
    pagination = Paginator(queryset, page_size)
    page_number = self.request.GET.get('page')
    page_obj = pagination.get_page(page_number)
    return {'object_list': page_obj}


@method_decorator(client_protected, name='dispatch')
class OrderListView(ListView):
    model = Order
    template_name = 'client/order_list.html'

    def get_queryset(self):
        return self.model.objects.filter(
            ~Q(order_status="cancelled") & ~Q(payment_status="cancelled") & Q(client=self.request.user)
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(get_paginated_context_data(self, self.get_queryset()))
        return context


@method_decorator(client_protected, name='dispatch')
class OrderCancelListView(ListView):
    model = Order
    template_name = 'client/order_cancel_list.html'

    def get_queryset(self):
        return self.model.objects.filter(
            Q(order_status="cancelled") | Q(payment_status="cancelled"),
            client=self.request.user
        )

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(get_paginated_context_data(self, self.get_queryset()))
        return context


@method_decorator(client_protected, name='dispatch')
class OrderDetailView(DetailView):
    model = Order
    template_name = 'client/order_detail.html'

    def get_queryset(self):
        return self.model.objects.filter(client=self.request.user)


class ShipmentDetailView(DetailView):
    model = Shipment
    template_name = 'client/shipment_detail.html'

    def get_queryset(self):
        return self.model.objects.filter(order__client=self.request.user)


@method_decorator(client_protected, name='dispatch')
class OrderInvoiceDetailView(DetailView):
    model = Order
    template_name = 'client/order_invoice.html'

    def get_object(self, queryset=None):
        order = get_object_or_404(Order, id=self.kwargs.get('pk'))
        return order


@method_decorator(client_protected, name='dispatch')
class ShipRocketShipment(View):
    template_name = 'client/shiprocket_shipment.html'

    def get(self, request, *args, **kwargs):
        shipment_id = self.kwargs.get('pk')
        shipment_detail, status_code = track_shipping(shipment_id)
        if not status_code == 200:
            error_message = shipment_detail['message']
            messages.error(self.request, error_message)
            return redirect("client:order_list")
        shipment_detail = shipment_detail.text
        shipment_detail = json.loads(shipment_detail)
        first_key = list(shipment_detail.keys())[0]
        shipment_detail = shipment_detail[first_key]['tracking_data']
        return render(self.request, template_name=self.template_name, context={'shipment_data': shipment_detail})


@method_decorator(client_protected, name='dispatch')
class WishCreateView(View):
    def get(self, request, pk):
        wishlist = Wishlist.objects.filter(user=self.request.user, product_id=pk)
        wish = wishlist.exists()
        product = Product.objects.get(id=pk)
        if wish:
            messages.success(request, 'Already in Wish List')
            print('hello')
            return redirect('website:product-detail', product.slug)
        wishlist = Wishlist.objects.create(user=self.request.user, product_id=pk)
        messages.success(request, 'Added to wishlist')
        return redirect('website:product-detail', product.slug)


@method_decorator(client_protected, name='dispatch')
class WishlistView(ListView):
    model = Wishlist
    template_name = 'client/wishlist_list.html'

    def get_queryset(self):
        return self.model.objects.filter(user=self.request.user)


@method_decorator(client_protected, name='dispatch')
class WishListDelete(View):
    def get(self, request, pk, *args, **kwargs):
        wishlist = get_object_or_404(Wishlist, user=self.request.user)
        wishlist.delete()
        messages.success(request, 'Wishlist Item Deleted Success Fully')
        return redirect("client:wishlist")


@method_decorator(client_protected, name='dispatch')
class PaymentListView(ListView):
    model = Payment
    template_name = 'client/payment_list.html'

    def get_queryset(self):
        return self.model.objects.filter(order__client=self.request.user)


@method_decorator(client_protected, name='dispatch')
class ProductRatingListView(ListView):
    model = ProductRating
    template_name = 'client/productrating_list.html'

    def get_queryset(self):
        rated_products_subquery = ProductRating.objects.filter(
            client=self.request.user,
            product_id=OuterRef('product_id'),
            order_id=OuterRef('order_id')
        ).values('product_id')
        order_items_without_review = OrderItem.objects.filter(
            order__client=self.request.user
        ).exclude(
            product_id__in=Subquery(rated_products_subquery)
        )
        return order_items_without_review


class ProductRatingCreateView(CreateView):
    model = ProductRating
    fields = ['rate', 'comment']
    template_name = 'client/productrating_form.html'

    def form_valid(self, form, *args, **kwargs):
        rate = form.cleaned_data.get('rate')
        comment = form.cleaned_data.get('comment')
        if not rate or not comment:
            messages.error(self.request, 'Please Enter Rate And Comment')
            return redirect('client:add-review', product_id=self.kwargs.get('product_id'),
                            order_id=self.kwargs.get('order_id'))
        if rate > 5:
            messages.error(self.request, 'Rate Must be less than 6')
            return redirect('client:add-review', product_id=self.kwargs.get('product_id'),
                            order_id=self.kwargs.get('order_id'))

        form.instance.product_id = self.kwargs.get('product_id')
        form.instance.order_id = self.kwargs.get('order_id')
        form.instance.client = self.request.user
        form.save()
        calculate_reviews(rate, self.kwargs.get('product_id'))
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('client:reviews')


@method_decorator(client_protected, name='dispatch')
class AddressList(TemplateView):
    # model = Order
    template_name = 'client/address.html'
    # context_object_name = 'objects'
    #
    # def get_queryset(self):
    #     return self.model.objects.filter(user=self.request.user)


@method_decorator(client_protected, name='dispatch')
class PasswordCheck(View):
    def get(self, request, *args, **kwargs):
        if request.user.has_usable_password():
            return redirect("client:user-password-change")
        return redirect('client:user-password-set')


@method_decorator(client_protected, name='dispatch')
class PasswordSetView(PasswordSetView):
    template_name = 'client/password_set_form.html'
    success_url = reverse_lazy('client:user-password-set')

    def form_valid(self, form):
        response = super().form_valid(form)
        return response


@method_decorator(client_protected, name='dispatch')
class PasswordChangeView(PasswordChangeView):
    template_name = 'client/password_change_form.html'
    success_url = reverse_lazy('client:user-password-change')

    def form_valid(self, form):
        response = super().form_valid(form)
        return response
