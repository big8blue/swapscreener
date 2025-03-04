import requests

API_URL = "https://api.coindcx.com/exchange/v1/derivatives/futures/data/active_instruments?margin_currency_short_name[]=USDT"

response = requests.get(API_URL)

try:
    data = response.json()
    print(data)  # Print the raw API response
except Exception as e:
    print(f"Error parsing JSON: {e}")


