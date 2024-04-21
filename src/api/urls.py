from django.urls import path
from src.api.views import OrderDetailAPIView, ProductListAPIView, ProductDetailAPIView, CartItemListAPIView, \
    CartItemUpdateAPIView, DeleteCartItemAPIView, WishlistListAPIView, WishlistCreateAPIView, WishlistDeleteAPIView, \
    PurchasedItemListAPIView, OrderCreateAPIView, CartItemAddAPIView, HomeAPIView

app_name = 'api'

urlpatterns = [


    path('home/', HomeAPIView.as_view(), name='home'),


    path('products/', ProductListAPIView.as_view(), name='product-list'),
    path('product/<str:pk>/', ProductDetailAPIView.as_view(), name='product-detail'),


    path('cart/list/', CartItemListAPIView.as_view(), name='cart-list'),
    path('cart/add/', CartItemAddAPIView.as_view(), name='cart-add'),
    path('cart/<str:pk>/update/', CartItemUpdateAPIView.as_view(),
         name='cart-update'),
    path('cart/<str:pk>/delete/', DeleteCartItemAPIView.as_view(), name='cart-delete'),


    path('wishlist/list/', WishlistListAPIView.as_view(), name='wishlist_list'),
    path('wishlist/add/', WishlistCreateAPIView.as_view(), name='wishlist_add'),
    path('wishlist/<int:wishlist_item_id>/remove/', WishlistDeleteAPIView.as_view(), name='wishlist_remove'),



]

urlpatterns += [
    path('api/purchased-items/', PurchasedItemListAPIView.as_view(), name='purchased_items'),
    path('orders/create/', OrderCreateAPIView.as_view(), name='order_create'),
    path('orders/detail/', OrderDetailAPIView.as_view(), name='order_detail'),
]
