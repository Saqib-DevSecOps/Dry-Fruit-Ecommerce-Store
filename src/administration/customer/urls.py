from django.urls import path

from src.administration.customer import views

app_name = 'customer'
urlpatterns = [
    path('api/purchased-items/', views.PurchasedItemListAPIView.as_view(), name='purchased_items'),
    path('orders/create/', views.OrderCreateAPIView.as_view(), name='order_create'),
    path('orders/detail/', views.OrderDetailAPIView.as_view(), name='order_detail'),
]
