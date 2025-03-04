import json
import websocket
import requests
import os
from dotenv import load_dotenv

# Load API Keys securely from .env
load_dotenv()
API_KEY = os.getenv("COINDCX_API_KEY")

# Get user input for trading pair
TRADE_SYMBOL = input("Enter the futures trading pair (e.g., JASMYUSDT): ").strip().upper()

# CoinDCX Futures WebSocket URL
WS_URL = "wss://public.coindcx.com"

def fetch_funding_rate(symbol):
    """Fetch current funding rate for the futures pair."""
    url = f"https://api.coindcx.com/exchange/v1/funding_rate?symbol={symbol}"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json().get("funding_rate", "N/A")
    return "N/A"

def on_message(ws, message):
    """Process real-time futures data from WebSocket."""
    data = json.loads(message)

    # Extract relevant data
    price = float(data.get('p', 0))
    volume = float(data.get('v', 0))
    bid_price = float(data.get('b', 0))
    ask_price = float(data.get('a', 0))
    funding_rate = fetch_funding_rate(TRADE_SYMBOL)

    # Display real-time futures data
    print(f"\n🔹 **{TRADE_SYMBOL} Futures Data** 🔹")
    print(f"📌 Current Price: ${price}")
    print(f"📈 Bid Price: ${bid_price}  |  📉 Ask Price: ${ask_price}")
    print(f"💰 24h Volume: {volume}")
    print(f"⚡ Funding Rate: {funding_rate}%")
    print("-" * 40)

def start_websocket():
    """Start real-time market data feed."""
    ws = websocket.WebSocketApp(WS_URL, on_message=on_message)
    ws.run_forever()

if __name__ == "__main__":
    print(f"📡 Connecting to CoinDCX WebSocket for {TRADE_SYMBOL} futures...")
    start_websocket()
