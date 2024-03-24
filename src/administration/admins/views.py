from django.contrib import messages
from django.core.paginator import Paginator
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import AdminPasswordChangeForm, PasswordChangeForm
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views import View
from django.views.generic import (
    TemplateView, ListView, DetailView, UpdateView, DeleteView,
    CreateView
)

from src.accounts.decorators import admin_protected
from src.accounts.models import User
from src.administration.admins.filters import UserFilter, ProductFilter, OrderFilter, BlogFilter
from src.administration.admins.forms import  ProductImageForm, MyProfileForm
from src.administration.admins.models import ProductCategory, BlogCategory, Product, ProductImage, Order, Blog, \
    Language

""" MAIN """


@method_decorator(admin_protected, name='dispatch')
class DashboardView(TemplateView):
    template_name = 'admins/dashboard.html'

    def get_context_data(self, **kwargs):
        context = super(DashboardView, self).get_context_data(**kwargs)
        context['blogs'] = Blog.objects.count()
        context['orders'] = Order.objects.count()
        context['users'] = User.objects.filter(is_staff=False).count()
        context['products'] = Product.objects.count()
        return context


@method_decorator(admin_protected, name='dispatch')
class UserOwnUpdateView(View):
    def get(self, request):
        form = MyProfileForm(instance=request.user)
        context = {'form': form}
        return render(request, template_name='admins/my-profile-change.html', context=context)

    def post(self, request):
        form = MyProfileForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            messages.success(request, "Your profile updated successfully")
            form.save(commit=True)
        context = {'form': form}
        return render(request, template_name='admins/my-profile-change.html', context=context)


@method_decorator(admin_protected, name='dispatch')
class UserOwnPasswordChangeView(View):

    def get(self, request):
        form = PasswordChangeForm(request.user)
        context = {'form': form}
        return render(request, template_name='admins/my-password-change.html', context=context)

    def post(self, request):
        form = PasswordChangeForm(user=request.user, data=request.POST or None)
        if form.is_valid():
            messages.success(request, "Your password changed successfully")
            form.save(commit=True)
        context = {'form': form}
        return render(request, template_name='admins/my-password-change.html', context=context)


""" USER MGMT"""


@method_decorator(admin_protected, name='dispatch')
class UserListView(ListView):
    queryset = User.objects.all()
    template_name = 'admins/user_list.html'
    paginate_by = 50

    def get_context_data(self, **kwargs):
        context = super(UserListView, self).get_context_data(**kwargs)
        _filter = UserFilter(self.request.GET, queryset=User.objects.filter())
        context['filter_form'] = _filter.form

        paginator = Paginator(_filter.qs, 50)
        page_number = self.request.GET.get('page')
        page_object = paginator.get_page(page_number)

        context['object_list'] = page_object
        return context


@method_decorator(admin_protected, name='dispatch')
class UserUpdateView(UpdateView):
    model = User
    fields = ['profile_image', 'first_name', 'last_name', 'email', 'username', 'is_staff', 'is_client', 'is_active']
    template_name = 'admins/user_form.html'
    success_url = reverse_lazy('admins:user-list')

    def get_success_url(self):
        return reverse_lazy('admins:user-detail', args=(self.object.pk,))


@method_decorator(admin_protected, name='dispatch')
class UserCreateView(CreateView):
    model = User
    fields = ['profile_image', 'first_name', 'last_name', 'email', 'username', 'is_active']
    template_name = 'admins/user_form.html'
    success_url = reverse_lazy('admins:user-list')

    def get_success_url(self):
        return reverse_lazy('admins:user-detail', args=(self.object.pk,))


@method_decorator(admin_protected, name='dispatch')
class UserDeleteView(DeleteView):
    model = User
    template_name = 'admins/user_confirm_delete.html'
    success_url = reverse_lazy('admins:user-list')


@method_decorator(admin_protected, name='dispatch')
class UserDetailView(DetailView):
    model = User
    template_name = 'admins/user_detail.html'


@method_decorator(admin_protected, name='dispatch')
class UserPasswordResetView(View):
    model = User
    template_name = 'admins/user_password_change.html'
    success_url = reverse_lazy('admins:user-list')
    context = {}

    def get(self, request, pk):
        user = get_object_or_404(User, pk=pk)
        form = AdminPasswordChangeForm(user=user)
        return render(request, self.template_name, {'form': form})

    def post(self, request, pk):
        user = get_object_or_404(User, pk=pk)
        form = AdminPasswordChangeForm(data=request.POST, user=user)
        if form.is_valid():
            form.save(commit=True)
            messages.success(request, f"{user.get_full_name()}'s password changed successfully.")
            return redirect('admins:user-detail', user.pk)

        return render(request, self.template_name, {'form': form})


""" MANAGEMENT """


@method_decorator(admin_protected, name='dispatch')
class CategoryListView(ListView):
    queryset = ProductCategory.objects.all()


@method_decorator(admin_protected, name='dispatch')
class CategoryUpdateView(UpdateView):
    model = ProductCategory
    fields = ['name', 'is_active']
    success_url = reverse_lazy('admins:category-list')


@method_decorator(admin_protected, name='dispatch')
class CategoryCreateView(CreateView):
    model = ProductCategory
    fields = ['name', 'is_active']
    success_url = reverse_lazy('admins:category-list')


@method_decorator(admin_protected, name='dispatch')
class CategoryDeleteView(DeleteView):
    model = ProductCategory
    success_url = reverse_lazy('admins:category-list')


@method_decorator(admin_protected, name='dispatch')
class LanguageListView(ListView):
    queryset = Language.objects.all()


@method_decorator(admin_protected, name='dispatch')
class LanguageUpdateView(UpdateView):
    model = Language
    fields = ['name']
    success_url = reverse_lazy('admins:category-list')


@method_decorator(admin_protected, name='dispatch')
class LanguageCreateView(CreateView):
    model = Language
    fields = ['name']
    success_url = reverse_lazy('admins:category-list')


@method_decorator(admin_protected, name='dispatch')
class LanguageDeleteView(DeleteView):
    model = Language
    success_url = reverse_lazy('admins:category-list')


@method_decorator(admin_protected, name='dispatch')
class BlogCategoryListView(ListView):
    queryset = BlogCategory.objects.all()


@method_decorator(admin_protected, name='dispatch')
class BlogCategoryUpdateView(UpdateView):
    model = BlogCategory
    fields = ['name', 'parent', 'is_active']
    success_url = reverse_lazy('admins:post-category-list')


@method_decorator(admin_protected, name='dispatch')
class BlogCategoryCreateView(CreateView):
    model = BlogCategory
    fields = ['name', 'parent', 'is_active']
    success_url = reverse_lazy('admins:post-category-list')


@method_decorator(admin_protected, name='dispatch')
class BlogCategoryDeleteView(DeleteView):
    model = BlogCategory
    success_url = reverse_lazy('admins:post-category-list')


""" INVENTORY """


@method_decorator(admin_protected, name='dispatch')
class ProductListView(ListView):
    queryset = Product.objects.all()
    paginate_by = 16

    def get_context_data(self, **kwargs):
        context = super(ProductListView, self).get_context_data(**kwargs)
        _filter = ProductFilter(self.request.GET, queryset=Product.objects.filter())
        context['filter_form'] = _filter.form

        paginator = Paginator(_filter.qs, 16)
        page_number = self.request.GET.get('page')
        page_object = paginator.get_page(page_number)

        context['object_list'] = page_object
        return context


@method_decorator(admin_protected, name='dispatch')
class ProductUpdateView(UpdateView):
    model = Product
    fields = [
        'thumbnail_image', 'name',
        'categories','price',
        'description', 'is_active'
    ]
    success_url = reverse_lazy('admins:product-list')


@method_decorator(admin_protected, name='dispatch')
class ProductCreateView(CreateView):
    model = Product
    fields = [
        'thumbnail_image', 'name',
        'categories','price',
        'description', 'is_active'
    ]
    success_url = reverse_lazy('admins:product-list')


@method_decorator(admin_protected, name='dispatch')
class ProductDetailView(DetailView):
    model = Product

    def get_context_data(self, **kwargs):
        context = super(ProductDetailView, self).get_context_data(**kwargs)
        context['product_image_add_form'] = ProductImageForm()
        return context


@method_decorator(admin_protected, name='dispatch')
class ProductDeleteView(DeleteView):
    model = Product
    success_url = reverse_lazy('admins:product-list')




@method_decorator(admin_protected, name='dispatch')
class ProductImageAddView(View):

    def post(self, request, product_id):
        product = get_object_or_404(Product, pk=product_id)
        form = ProductImageForm(data=request.POST, files=request.FILES)
        if form.is_valid():
            form.instance.product = product
            form.save()
            messages.success(request, "Product Image added successfully")
        return redirect("admins:product-detail", product_id)


@method_decorator(admin_protected, name='dispatch')
class ProductImageDeleteView(View):

    def get(self, request, product_id, pk):
        product = get_object_or_404(Product, pk=product_id)
        product_image = get_object_or_404(ProductImage.objects.filter(product=product), pk=pk)
        product_image.delete()
        messages.success(request, "Product Image deleted successfully")
        return redirect("admins:product-detail", product_id)

    def post(self, request, product_id, pk):
        product = get_object_or_404(Product, pk=product_id)
        product_image = get_object_or_404(ProductImage.objects.filter(product=product), pk=pk)
        product_image.delete()
        messages.success(request, "Product Image deleted successfully")
        return redirect("admins:product-detail", product_id)


""" ORDERS """


@method_decorator(admin_protected, name='dispatch')
class OrderListView(ListView):
    queryset = Order.objects.all()
    paginate_by = 25

    def get_context_data(self, **kwargs):
        context = super(OrderListView, self).get_context_data(**kwargs)
        _filter = OrderFilter(self.request.GET, queryset=Order.objects.filter())
        context['filter_form'] = _filter.form

        paginator = Paginator(_filter.qs, 25)
        page_number = self.request.GET.get('page')
        page_object = paginator.get_page(page_number)

        context['object_list'] = page_object
        return context


@method_decorator(admin_protected, name='dispatch')
class OrderDetailView(DetailView):
    model = Order

    def get_context_data(self, **kwargs):
        context = super(OrderDetailView, self).get_context_data(**kwargs)
        context['orders'] = Order.objects.filter(pk=self.object.pk)
        return context


@method_decorator(admin_protected, name='dispatch')
class OrderDeleteView(DeleteView):
    model = Order
    success_url = reverse_lazy('admins:Order-list')


@method_decorator(admin_protected, name='dispatch')
class OrderStatusChangeView(View):

    def get(self, request, pk):
        pass


""" BLOG """


@method_decorator(admin_protected, name='dispatch')
class BlogListView(ListView):
    queryset = Blog.objects.all()
    paginate_by = 16

    def get_context_data(self, **kwargs):
        context = super(BlogListView, self).get_context_data(**kwargs)
        _filter = BlogFilter(self.request.GET, queryset=Blog.objects.filter())
        context['filter_form'] = _filter.form

        paginator = Paginator(_filter.qs, 16)
        page_number = self.request.GET.get('page')
        page_object = paginator.get_page(page_number)

        context['object_list'] = page_object
        return context


@method_decorator(admin_protected, name='dispatch')
class BlogDetailView(DetailView):
    model = Blog


@method_decorator(admin_protected, name='dispatch')
class BlogDeleteView(DeleteView):
    model = Blog
    success_url = reverse_lazy('admins:post-list')


@method_decorator(admin_protected, name='dispatch')
class BlogUpdateView(UpdateView):
    model = Blog
    fields = [
        'thumbnail_image', 'title', 'category', 'read_time', 'content', 'status'
    ]
    success_url = reverse_lazy('admins:post-list')


@method_decorator(admin_protected, name='dispatch')
class BlogCreateView(CreateView):
    model = Blog
    fields = [
        'thumbnail_image', 'title', 'category', 'read_time', 'content', 'status'
    ]
    success_url = reverse_lazy('admins:post-list')

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super(BlogCreateView, self).form_valid(form)
