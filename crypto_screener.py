import requests

url = "https://api.coindcx.com/exchange/v1/derivatives/futures/data/active_instruments"
response = requests.get(url)

if response.status_code == 200:
    print("✅ API Connection Successful!")
    print(response.json())  # Print the fetched data
else:
    print("❌ API Error:", response.status_code, response.text)
