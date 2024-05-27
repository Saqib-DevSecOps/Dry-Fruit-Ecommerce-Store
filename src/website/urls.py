from django.urls import path

from src.website.views import HomeTemplateView, \
    ContactUsTemplateView, BlogListView, CartTemplateView, AboutUsTemplateView, \
    ProductListView, ProductDetailView, BlogDetailView, AddToCart, \
    RemoveFromCartView, OrderCreate, SuccessPayment, CancelPayment, CookiePolicy, PrivacyPolicy, \
    TermsAndCondition, Jobs, ReturnPolicy, ShippingPolicy, WishListListView, UpdateCart, AddToWishlist, \
    DeleteFromWishlist, BuyNow, FranchiseTemplateView, ShipmentPriceRetrieveView

app_name = "website"
urlpatterns = [
    path('', HomeTemplateView.as_view(), name='home'),
    path('shop/', ProductListView.as_view(), name='shop'),
    path('product-detail/<str:pk>', ProductDetailView.as_view(), name='product-detail'),
    path('blogs/', BlogListView.as_view(), name='posts'),
    path('blog-detail/<str:pk>', BlogDetailView.as_view(), name='post-detail'),

    path('about-us/', AboutUsTemplateView.as_view(), name='about_us'),
    path('contact-us/', FranchiseTemplateView.as_view(), name='franchise'),
    path('Franchise/', ContactUsTemplateView.as_view(), name='contact_us'),

    path('cart/', CartTemplateView.as_view(), name='cart'),
    path('add-to-cart/<str:product_id>/<str:product_weight_id>/', AddToCart.as_view(), name='add-to-cart'),
    path('buy-now/<str:product_id>/<str:product_weight_id>/', BuyNow.as_view(), name='buy-now'),
    path('remove-cart/<str:pk>/', RemoveFromCartView.as_view(), name='remove-cart'),
    path('increment/cart/item/<str:id>/<str:quantity>/', UpdateCart.as_view(), name='update-cart'),

    path('wishlist/', WishListListView.as_view(), name='wishlist_list'),
    path('wishlist/add/<str:pk>/', AddToWishlist.as_view(), name='wishlist-add'),
    path('wishlist/delete/<str:pk>', DeleteFromWishlist.as_view(), name='wishlist-delete'),

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

urlpatterns += [
    path('get-shpment_price', ShipmentPriceRetrieveView.as_view(), name='shipment_retrieve'),

]
