import requests
import json

url = "https://apiv2.shiprocket.in/v1/external/auth/login"

payload = json.dumps({
  "email": "saqib71501@gmail.com",
  "password": "saqib71501@gmail.com"
})
headers = {
  'Content-Type': 'application/json'
}

response = requests.request("POST", url, headers=headers, data=payload)

print(response.text)
