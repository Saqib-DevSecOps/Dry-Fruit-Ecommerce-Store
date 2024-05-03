from django.urls import path

from src.apps.razorpay.views import paymenthandler, CreateRazorPayCheckout

app_name = 'razorpay'

urlpatterns = [
    path('pay/now/<str:pk>/', CreateRazorPayCheckout.as_view(), name='pay'),
    path('paymenthandler/', paymenthandler, name='payment_handler'),
]
