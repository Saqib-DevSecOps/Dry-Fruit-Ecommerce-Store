from django.urls import path, include
from .views import (
    WishlistListCreateAPIView, WishlistDeleteAPIView,
    BuyerDashboardAPIView,
    OrderListAPIView, OrderDetailAPIView, ProductRatingAddAPIView, OrderCreateApiView,

    CartRetrieveUpdateDestroyAPIView, CartListCreateAPIView, HomeProductsListAPIView,
    ProductListAPIView, ProductDetailAPIView, PaymentSuccessAPIView, ProductPendingRatingListView,
    ShipmentRetrieveAPIView, ShipRocketShipmentRetrieveAPIView, ApplyCouponCode, CouponListAPIView, RatingListAPIView,
    BuyerAddressListCreateApiView, BuyerAddressUpdateDeleteApiView
)

app_name = 'api'
urlpatterns = [
    path('home/', HomeProductsListAPIView.as_view(), name='home'),
]

urlpatterns += [
    path('cart/items/', CartListCreateAPIView.as_view(), name='cart'),
    path('cart/<int:pk>/', CartRetrieveUpdateDestroyAPIView.as_view(), name='cart-retrieve-update-destroy'),
]

urlpatterns += [
    path('product/', ProductListAPIView.as_view(), name='product-list'),
    path('product/<str:pk>/', ProductDetailAPIView.as_view(), name='product-detail'),
]

urlpatterns += [
    path('wish-list/', WishlistListCreateAPIView.as_view(), name='wishlist'),
    path('wish-list/<str:pk>/delete/', WishlistDeleteAPIView.as_view(), name='remove-from-wishlist'),
]

urlpatterns += [
    path('coupon-list/', CouponListAPIView.as_view(), name='coupon-list'),
    path('apply-coupon/', ApplyCouponCode.as_view(), name='apply-coupon'),
]

urlpatterns += [
    path('dashboard/', BuyerDashboardAPIView.as_view(), name='dashboard'),
    path('order/', OrderListAPIView.as_view(), name='order-list'),
    path('order/<str:pk>/', OrderDetailAPIView.as_view(), name='order-detail'),

    path('checkout/', OrderCreateApiView.as_view(), name='checkout'),
    path('pending/reviews/', ProductPendingRatingListView.as_view(), name='product-rating-pending-list'),
    path('rating/list/', RatingListAPIView.as_view(), name='rating-list'),
    path('order/add/rating/', ProductRatingAddAPIView.as_view(), name='product-rating-add'),
    path('payment/success/', PaymentSuccessAPIView.as_view(), name='payment/success/'),

    path('shipment-detail/<str:pk>/', ShipmentRetrieveAPIView.as_view(), name="custom_shipment"),
    path('shiprocket/shipment-detail/<str:pk>/', ShipRocketShipmentRetrieveAPIView.as_view(),
         name="shiprocket_shipment")

]

urlpatterns += [
    path('address/', BuyerAddressListCreateApiView.as_view(), name="address"),
    path('address/<str:pk>/', BuyerAddressUpdateDeleteApiView.as_view(), name="address"),

]

urlpatterns += [
    path('accounts/', include('src.api.accounts.urls', namespace='accounts')),
]
