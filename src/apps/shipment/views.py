from django.contrib import messages
from django.contrib.sites import requests
from django.http import JsonResponse
from django.shortcuts import redirect
from django.views import View
from rest_framework.utils import json

from src.apps.shipment.bll import get_or_refresh_token, create_shiprocket_order


# Shipment Views for Ship Rocket

class ShipmentCreateOrderView(View):
    def post(self, request):
        token = get_or_refresh_token()
        if token:
            order_data = json.dumps({
                "order_id": "224-447",
                "order_date": "2019-07-24 11:11",
                "pickup_location": "Jammu",
                "channel_id": "",
                "comment": "Reseller: M/s Goku",
                "billing_customer_name": "Naruto",
                "billing_last_name": "Uzumaki",
                "billing_address": "House 221B, Leaf Village",
                "billing_address_2": "Near Hokage House",
                "billing_city": "New Delhi",
                "billing_pincode": "110002",
                "billing_state": "Delhi",
                "billing_country": "India",
                "billing_email": "naruto@uzumaki.com",
                "billing_phone": "9876543210",
                "shipping_is_billing": True,
                "shipping_customer_name": "",
                "shipping_last_name": "",
                "shipping_address": "",
                "shipping_address_2": "",
                "shipping_city": "",
                "shipping_pincode": "",
                "shipping_country": "",
                "shipping_state": "",
                "shipping_email": "",
                "shipping_phone": "",
                "order_items": [
                    {
                        "name": "Kunai",
                        "sku": "chakra123",
                        "units": 10,
                        "selling_price": "900",
                        "discount": "",
                        "tax": "",
                        "hsn": 441122
                    }
                ],
                "payment_method": "Prepaid",
                "shipping_charges": 0,
                "giftwrap_charges": 0,
                "transaction_charges": 0,
                "total_discount": 0,
                "sub_total": 9000,
                "length": 10,
                "breadth": 15,
                "height": 20,
                "weight": 2.5
            })
            # response = create_shiprocket_order(token, order_data)
            response = True
            if response:
                messages.success(request, "Order created for shipment")
                return redirect('success-page-url')
            else:
                error_message = "Something went wrong"
                if 'errors' in response:
                    error_message = ", ".join(response['errors'].values())
                messages.error(request, error_message)
                return redirect('failure-page-url')
        else:
            return redirect('token-error-page-url')
