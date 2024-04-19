from django.urls import path

from src.website.views import HomeTemplateView, \
    ContactUsTemplateView, BlogListView, CartTemplateView, AboutUsTemplateView, \
    ProductListView, ProductDetailView, BlogDetailView, AddToCart, IncrementCart, DecrementCart, \
    RemoveFromCartView, OrderCreate, SuccessPayment, CancelPayment, CookiePolicy, PrivacyPolicy, \
    TermsAndCondition, Jobs, ReturnPolicy, ShippingPolicy, WishListListView

app_name = "website"
urlpatterns = [
    path('', HomeTemplateView.as_view(), name='home'),
    path('shop/', ProductListView.as_view(), name='shop'),
    path('product-detail/<str:pk>', ProductDetailView.as_view(), name='product-detail'),
    path('blogs/', BlogListView.as_view(), name='posts'),
    path('blog-detail/<str:slug>', BlogDetailView.as_view(), name='post-detail'),

    path('about-us/', AboutUsTemplateView.as_view(), name='about_us'),
    path('contact-us/', ContactUsTemplateView.as_view(), name='contact_us'),

    path('cart/', CartTemplateView.as_view(), name='cart'),
    path('add_to_cart/<str:product_id>/', AddToCart.as_view(), name='add-to-cart'),
    path('remove-cart/', RemoveFromCartView.as_view(), name='remove-cart'),
    path('increment/cart/item', IncrementCart.as_view(), name='increment'),
    path('decrement/cart/item', DecrementCart.as_view(), name='decrement'),

    path('wishlist/', WishListListView.as_view(), name='wishlist_list'),

    path('billing', OrderCreate.as_view(), name='order'),
    path('payment-success/', SuccessPayment.as_view(), name="success"),
    path('payment-cancelled/', CancelPayment.as_view(), name="cancel"),


    path('cookie-policy/', CookiePolicy.as_view(), name='cookie'),
    path('privacy-policy/', PrivacyPolicy.as_view(), name='privacy'),
    path('terms-and-conditions/', TermsAndCondition.as_view(), name='terms'),
    path('jobs/', Jobs.as_view(), name='jobs'),
    path('return-policy/', ReturnPolicy.as_view(), name='return_policy'),
    path('shipping-policy/', ShippingPolicy.as_view(), name='shipping_policy')
]
