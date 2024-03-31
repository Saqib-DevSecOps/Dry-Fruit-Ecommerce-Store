from django.urls import path

from src.administration.client.views import ClientDashboard, WishlistView, WishListDelete, UserUpdateView, \
    AddressUpdate, WishCreateView, OrderListView, AddressList, OrderCancelListView, OrderDetailView

app_name = 'client'
urlpatterns = [
    path('', ClientDashboard.as_view(), name='dashboard'),

    path('wishlist/', WishlistView.as_view(), name='wishlist'),
    path('wishlist/create/<str:pk>', WishCreateView.as_view(), name='wishlist-create'),
    path('wishlist/delete/<str:pk>', WishListDelete.as_view(), name='wishlist-delete'),

    path('my-orders/', OrderListView.as_view(), name='order_list'),
    path('cancel-orders/', OrderCancelListView.as_view(), name='cancel_order'),
    path('order-detail/', OrderDetailView.as_view(), name='order_detail'),

    path('my-address/', AddressList.as_view(), name='address'),

    path('user/change/', UserUpdateView.as_view(), name='user-change'),
    path('user/address/update/<str:pk>', AddressUpdate.as_view(), name='user-address-update'),

]
