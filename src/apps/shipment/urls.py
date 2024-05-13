from django.urls import path

from src.apps.shipment.views import ShipmentCreateOrderView

app_name = 'shipment'

# Shipment Urls for Ship Rocket

urlpatterns = [
    path('create-order/', ShipmentCreateOrderView.as_view(), name='shipment-create-order')
]
