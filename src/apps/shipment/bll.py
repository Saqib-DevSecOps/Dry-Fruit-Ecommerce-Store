import json
import os

import requests

from src.administration.admins.models import Order


# Getting Token
def get_or_refresh_token():
    email = "saqibahmad77866@gmail.com"
    password = "Admin@123"

    if email and password:
        url = "https://apiv2.shiprocket.in/v1/external/auth/login"
        payload = {
            "email": email,
            "password": password
        }
        headers = {
            'Content-Type': 'application/json'
        }
        response = requests.post(url, headers=headers, json=payload)
        if response.status_code == 200:
            return response.json().get('token')
    return None


def add_new_pickup_location(form):
    token = get_or_refresh_token()
    url = "https://apiv2.shiprocket.in/v1/external/settings/company/addpickup"
    payload = {
        "pickup_location": form.cleaned_data['pickup_location'],
        "name": form.cleaned_data['name'],
        "email": form.cleaned_data['email'],
        "phone": form.cleaned_data['phone'],
        "address": form.cleaned_data['address'],
        "address_2": form.cleaned_data['address_2'],
        "city": form.cleaned_data['city'],
        "state": form.cleaned_data['state'],
        "country": form.cleaned_data['country'],
        "pin_code": form.cleaned_data['pin_code'],
    }

    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {token}'
    }
    response = requests.post(url, headers=headers, json=payload)
    return response


# Orders Function
def create_shiprocket_order(form, order):
    token = get_or_refresh_token()
    url = "https://apiv2.shiprocket.in/v1/external/orders/create/adhoc"
    created_on_formatted = order.created_on.strftime("%Y-%m-%d %H:%M")
    payload = json.dumps({
        "order_id": order.id,
        "order_date": created_on_formatted,
        "pickup_location": str(form.cleaned_data['pickup_location']),
        "billing_customer_name": str(order.full_name),
        "billing_last_name": "",
        "billing_address": str(order.address),
        "billing_city": str(order.city),
        "billing_pincode": str(order.postal_code),
        "billing_state": str(order.state),
        "billing_country": str(order.country),
        "billing_email": str(order.client.email),
        "billing_phone": str(order.contact),
        "shipping_is_billing": True,
        "order_items": [
            {
                "name": item.product.title,
                "sku": f"{item.product.sku}_{item.product.pk}_{counter}",
                "units": item.qty,
                "selling_price": str(item.product.get_price()),
            }
            for counter, item in enumerate(order.get_cart(), start=1)
        ],
        "payment_method": "Prepaid",
        "sub_total": float(order.sub_total),
        "length": float(form.cleaned_data['length']),
        "breadth": float(form.cleaned_data['breadth']),
        "height": float(form.cleaned_data['height']),
        "weight": float(form.cleaned_data['weight'])
    })
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {token}'
    }
    response = requests.request("POST", url, headers=headers, data=payload)

    return response


def generate_awb_for_shipment(shipment_id):
    token = get_or_refresh_token()
    url = "https://apiv2.shiprocket.in/v1/external/courier/assign/awb"
    payload = json.dumps({
        "shipment_id": str(shipment_id),
    })
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {token}'
    }
    response = requests.request("POST", url, headers=headers, data=payload)
    return response


def request_for_shipment_pickup(shipment_id):
    token = get_or_refresh_token()
    url = "https://apiv2.shiprocket.in/v1/external/courier/generate/pickup"
    payload = json.dumps({
        "shipment_id": str(shipment_id),
    })
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {token}'
    }
    response = requests.request("POST", url, headers=headers, data=payload)
    return response


def get_shipment_detail(shipment_id):
    token = get_or_refresh_token()
    print(shipment_id)
    url = f"https://apiv2.shiprocket.in/v1/external/shipments/{shipment_id}"
    payload = {}
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {token}'
    }
    response = requests.request("GET", url, headers=headers, data=payload)
    return response
