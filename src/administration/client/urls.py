from django.urls import path

from src.administration.client.views import ClientDashboard, WishlistView, WishListDelete, UserUpdateView, \
    AddressUpdate, WishCreateView, OrderListView, AddressList, OrderCancelListView, OrderDetailView, PasswordCheck, \
    PasswordSetView, PasswordChangeView, PaymentListView, ShipmentDetailView, ShipRocketShipment, ProductRatingListView, \
    ProductRatingCreateView

app_name = 'client'
urlpatterns = [
    path('', ClientDashboard.as_view(), name='dashboard'),

    path('wishlist/', WishlistView.as_view(), name='wishlist'),
    path('wishlist/create/<str:pk>', WishCreateView.as_view(), name='wishlist-create'),
    path('wishlist/delete/<str:pk>', WishListDelete.as_view(), name='wishlist-delete'),

    path('reviews/', ProductRatingListView.as_view(), name='reviews'),
    path('review/add/<str:product_id>/<str:order_id>/', ProductRatingCreateView.as_view(), name='add-review'),

    path('my-orders/', OrderListView.as_view(), name='order_list'),
    path('cancel-orders/', OrderCancelListView.as_view(), name='cancel_order'),
    path('order-detail/<str:pk>/', OrderDetailView.as_view(), name='order_detail'),
    path('shipment-detail/<str:pk>/', ShipmentDetailView.as_view(), name='shipment_detail'),
    path('r/shipment-detail/<str:pk>/', ShipRocketShipment.as_view(), name='shiprocket_shipment_detail'),
    path('payment/list/', PaymentListView.as_view(), name="payment-list"),

    path('my-address/', AddressList.as_view(), name='address'),

    path('user/change/', UserUpdateView.as_view(), name='user-change'),
    path('user/address/update/<str:pk>', AddressUpdate.as_view(), name='user-address-update'),

    path('user/password/check/', PasswordCheck.as_view(), name="user-password-check"),
    path('user/password/set/', PasswordSetView.as_view(), name="user-password-set"),
    path('user/password/change/', PasswordChangeView.as_view(), name="user-password-change"),

]
