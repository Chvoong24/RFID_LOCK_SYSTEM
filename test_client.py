import requests

server_url = "http://127.0.0.1:5000/search_tag"

try:
    response = requests.post(server_url)
    if response.ok:
        print("Response:", response.json())
    else:
        print(f"Error {response.status_code}: {response.text}")
except Exception as e:
    print(f"Error connecting to server: {e}")
