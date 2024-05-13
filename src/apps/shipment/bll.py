import os

import requests


# Getting Token
def get_or_refresh_token():
    # TODO """ Later will get Email and Password from .env File"""
    # email = os.getenv('SHIP_ROCKET_EMAIL')
    # password = os.getenv('SHIP_ROCKET_PASSWORD')

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


# Orders Function
def create_shiprocket_order(token, order_data):
    url = "https://apiv2.shiprocket.in/v1/external/orders/create/adhoc"
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {token}'
    }
    response = requests.post(url, headers=headers, json=order_data)
    return response.json() if response.status_code == 200 else None


def get_all_orders(token):
    url = "https://apiv2.shiprocket.in/v1/external/orders"

    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {token}'
    }

    try:
        response = requests.get(url, headers=headers)

        if response.status_code == 200:
            orders = response.json()
            return orders
        else:
            print(f"Failed to fetch orders. Status code: {response.status_code}")
            return None
    except Exception as e:
        print(f"An error occurred: {e}")
        return None


def get_specific_order(order_id, token):
    url = f"https://apiv2.shiprocket.in/v1/external/orders/show/{order_id}"
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {token}',
    }

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        order_data = response.json()
        return order_data
    except requests.RequestException as e:
        print(f"Request failed: {e}")
        return None
