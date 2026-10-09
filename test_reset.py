import requests

url = "http://127.0.0.1:8000/api/password_reset/"
data = {"email": "e.rustamovv.09@gmail.com"}
try:
    response = requests.post(url, json=data)
    print(f"Status: {response.status_code}")
    print(f"Response: {response.text}")
except Exception as e:
    print(f"Error: {e}")
