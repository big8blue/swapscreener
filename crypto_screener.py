import requests
import json

API_URL = "https://api.coindcx.com/exchange/v1/derivatives/futures/data/active_instruments?margin_currency_short_name[]=USDT"

response = requests.get(API_URL)

if response.status_code == 200:
    print(json.dumps(response.json(), indent=2))  # Print formatted API response
else:
    print("Error:", response.status_code)

