from django.urls import path

from src.api import views

app_name = 'api'

urlpatterns = [
    path('products/', views.ProductListAPIView.as_view(), name='product-list'),
    path('products/<int:pk>/', views.ProductDetailAPIView.as_view(), name='product-detail'),
    path('cart/', views.CartItemListAPIView.as_view(), name='cart-list'),
    path('cart/add/', views.CartItemAPIView.as_view(), name='cart-add'),
    path('cart/increment/<int:increment_cart_item_id>/', views.IncrementCartItemAPIView.as_view(),
         name='cart-increment'),
    path('cart/decrement/<int:decrement_cart_item_id>/', views.DecrementCartItemAPIView.as_view(),
         name='cart-decrement'),
    path('cart/delete/<int:delete_cart_item_id>/', views.DeleteCartItemAPIView.as_view(), name='cart-delete'),

    path('post/list/', views.PostListAPIView.as_view(), name='post-list'),
    path('post/detail/<str:slug>/', views.PostDetailAPIView.as_view(), name='post-detail'),

    path('wishlist/', views.WishlistListAPIView.as_view(), name='wishlist_list'),
    path('wishlist/add/', views.WishlistCreateAPIView.as_view(), name='wishlist_add'),
    path('wishlist/<int:wishlist_item_id>/remove/', views.WishlistDeleteAPIView.as_view(), name='wishlist_remove'),



]

urlpatterns += [
    path('api/purchased-items/', views.PurchasedItemListAPIView.as_view(), name='purchased_items'),
    path('orders/create/', views.OrderCreateAPIView.as_view(), name='order_create'),
    path('orders/detail/', views.OrderDetailAPIView.as_view(), name='order_detail'),
]
