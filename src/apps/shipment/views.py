import requests


def calculate_volumetric_weight(length, width, height, divisor=5000):
    volumetric_weight = (length * width * height) / divisor
    return volumetric_weight


def get_chargeable_weight(actual_weight, volumetric_weight):
    return max(actual_weight, volumetric_weight)


def get_or_refresh_token():
    email = "hiren9016573094@gmail.com"
    password = "Hiren@007"

    if email and password:
        url = "https://apiv2.shiprocket.in/v1/external/auth/login"
        payload = {
            "email": email,
            "password": password
        }
        headers = {
            'Content-Type': 'application/json'
        }
        try:
            response = requests.post(url, headers=headers, json=payload)
            response.raise_for_status()
            return response.json().get('token')
        except requests.exceptions.RequestException as e:
            print(f"Error occurred while fetching or refreshing token: {e}")
    return None


def get_shipping_rate():
    token = get_or_refresh_token()
    url = "https://apiv2.shiprocket.in/v1/external/courier/serviceability/"

    payload = {
        "pickup_postcode": 110001,
        "delivery_postcode": 400001,
        "cod": 0,  # Change to 1 if COD is needed
        "weight": "20",
        "length": "20",
        "breadth": "23",
        "height": "34"
    }

    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {token}'
    }

    response = requests.request("GET", url, headers=headers, data=payload)
    print(response)
    print(response.text)
    print(response.json())
    return response.json()


get_shipping_rate()
