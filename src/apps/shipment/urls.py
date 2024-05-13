from django.urls import path

from src.apps.shipment.views import ShipmentCreateOrderView, ShipmentGetOrder, GetSpecificOrderView, GetAndSaveOrders

app_name = 'shipment'

# Shipment Urls for Ship Rocket

urlpatterns = [
    path('get-orders/', ShipmentGetOrder.as_view(), name='get-orders'),
    path('get-specific-order/<int:pk>', GetSpecificOrderView.as_view(), name='get-specific-order'),
    path('create-order/<int:pk>', ShipmentCreateOrderView.as_view(), name='shipment-create-order'),

    # Shipment urls
    path('reload-orders/', GetAndSaveOrders.as_view(), name='reload-orders')

]
