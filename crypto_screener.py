import asyncio
import json
import aiohttp
import websocket
import requests
import numpy as np
from collections import deque

# CoinDCX API Keys
API_KEY = "64fcb132c957dbfc1fd4db8f96d9cf69fb39684333abee29"
SECRET_KEY = "53866511d5f015b28cfaac863065eb75f9f0f9e26d5c905f890095604e7ca37d"

# WebSocket & API URLs
WS_URL = "wss://public.coindcx.com"

# Get user inputs
TRADE_SYMBOL = input("Enter the trading pair (e.g., JASMYUSDT): ").strip().upper()
LEVERAGE = int(input("Enter leverage (e.g., 10 for 10x): "))

# Minimum trade size ($6.05 per trade)
MIN_TRADE_SIZE_USD = 6.05  

# Trading Parameters
cumulative_volume = 0
volume_threshold = 50000  # Adjust based on market conditions
momentum_window = deque(maxlen=5)  # Tracks price momentum
order_book_depth = deque(maxlen=5)  # Tracks bid/ask imbalance

async def fetch_market_data():
    """Fetch market data for initial reference."""
    url = f"https://api.coindcx.com/market_data"
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            data = await response.json()
            return data

def get_trade_quantity(price):
    """Calculate quantity based on the minimum trade size of $6.05 per trade."""
    return round(MIN_TRADE_SIZE_USD / price, 4)  

def compute_momentum():
    """Check if the last 5 prices indicate an upward or downward trend."""
    if len(momentum_window) < 5:
        return None  # Not enough data
    diff = np.diff(momentum_window)
    return np.all(diff > 0) or np.all(diff < 0)  # True if trending up/down

def compute_order_book_imbalance():
    """Check if bid/ask imbalance favors buyers or sellers."""
    if len(order_book_depth) < 5:
        return None  # Not enough data
    avg_imbalance = np.mean(order_book_depth)
    return avg_imbalance > 0  # True if buy pressure, False if sell pressure

def place_order(order_type, price):
    """Place a trade with leverage."""
    quantity = get_trade_quantity(price) * LEVERAGE
    order_data = {
        "symbol": TRADE_SYMBOL,
        "side": order_type,
        "quantity": quantity,
        "order_type": "market"
    }
    response = requests.post("https://api.coindcx.com/trade", json=order_data, headers={"X-AUTH-APIKEY": API_KEY})
    if response.status_code == 200:
        print(f"✅ Order placed: {order_type} {quantity} {TRADE_SYMBOL} at {price} with {LEVERAGE}x leverage")
    else:
        print("❌ Order failed!")

def on_message(ws, message):
    """Process live market data."""
    global cumulative_volume
    data = json.loads(message)

    price = float(data['p'])
    volume = float(data['v'])
    bid_size = float(data.get('b', 0))  # Bid size from order book
    ask_size = float(data.get('a', 0))  # Ask size from order book

    # Update indicators
    cumulative_volume += volume
    momentum_window.append(price)
    order_book_depth.append(bid_size - ask_size)  # Positive = Buy pressure, Negative = Sell pressure

    # Compute signals
    is_trending = compute_momentum()
    is_buy_pressure = compute_order_book_imbalance()

    # Execute trade logic
    if cumulative_volume > volume_threshold and is_trending and is_buy_pressure:
        place_order("buy", price)
        cumulative_volume = 0  # Reset after trade

def start_websocket():
    """Start real-time market data feed."""
    ws = websocket.WebSocketApp(WS_URL, on_message=on_message)
    ws.run_forever()

if __name__ == "__main__":
    asyncio.run(fetch_market_data())
    start_websocket()
