api_user_email = "saqibahmad77866@gmail.com"
api_user_password = "Admin@123"

import requests
import json

url = "https://apiv2.shiprocket.in/v1/external/auth/login"

payload = json.dumps({
    "email": api_user_email,
    "password": api_user_password
})
headers = {
    'Content-Type': 'application/json'
}

try:
    response = requests.post(url, headers=headers, data=payload)
    response.raise_for_status()  # Raise an exception for 4xx or 5xx status codes
    token = response.json()["token"]
    print("Token:", token)
except requests.exceptions.RequestException as e:
    print("Request failed:", e)
    print("Response content:", response.content)
