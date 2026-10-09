import requests

url = "http://127.0.0.1:8000/api/token/"
data = {"username": "test", "password": "1"}  # we don't know the password
print(requests.post(url, json=data).text)
