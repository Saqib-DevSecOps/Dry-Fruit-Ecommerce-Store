import os

import requests


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


def create_shiprocket_order(token, order_data):
    url = "https://apiv2.shiprocket.in/v1/external/orders/create/adhoc"
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {token}'
    }
    response = requests.post(url, headers=headers, json=order_data)
    return response.json() if response.status_code == 200 else None
