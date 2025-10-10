import requests

url = "http://ip-api.com/json/"

try:
    response = requests.get(url)
    response.raise_for_status()

    data = response.json()

    print("IP Address:", data["query"])
    print("Country:", data["country"])
    print("Region:", data["regionName"])
    print("City:", data["city"])
    print("Latitude, Longitude:", data["lat"], ",", data["lon"])
    print("ISP:", data["isp"])

except requests.exceptions.RequestException as err:
    print(f"Request error: {err}")
except KeyError as key_err:
    print(f"Data parsing error: {key_err}")