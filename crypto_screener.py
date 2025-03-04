import asyncio
import json
import os
import aiohttp
import requests
import numpy as np
import websocket
from dotenv import load_dotenv
from collections import deque

# Load API Keys securely from .env
load_dotenv()
API_KEY = os.getenv("COINDCX_API_KEY")
SECRET_KEY = os.getenv("COINDCX_SECRET_KEY")

if not API_KEY or not SECRET_KEY:
    raise ValueError("API keys missing! Set them in the .env file.")

# Get user input for trading pair and leverage
TRADE_SYMBOL = input("Enter the trading pair (e.g., JASMYUSDT): ").strip().upper()
LEVERAGE = int(input("Enter leverage (e.g., 10 for 10x): "))

# Trading Parameters
MIN_TRADE_SIZE_USD = 6.05  # Min trade size per order
VOLUME_THRESHOLD = 50000  # Cumulative volume threshold
momentum_window = deque(maxlen=5)  # Price momentum tracking
order_book_depth = deque(maxlen=5)  # Bid/ask imbalance tracking
cumulative_volume = 0  # Initialize cumulative volume

async def fetch_market_data():
    """Fetch market data for initial reference."""
    url = "https://api.coindcx.com/market_data"
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            data = await response.json()
            return data

def get_trade_quantity(price):
    """Calculate quantity based on $6.05 per trade."""
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
    """Place a leveraged trade order."""
    quantity = get_trade_quantity(price) * LEVERAGE
    order_data = {
        "symbol": TRADE_SYMBOL,
        "side": order_type,
        "quantity": quantity,
        "order_type": "market"
    }
    headers = {"X-AUTH-APIKEY": API_KEY}
    response = requests.post("https://api.coindcx.com/trade", json=order_data, headers=headers)
    
    if response.status_code == 200:
        print(f"✅ Order placed: {order_type} {quantity} {TRADE_SYMBOL} at {price} with {LEVERAGE}x leverage")
    else:
        print(f"❌ Order failed: {response.json()}")

def on_message(ws, message):
    """Process real-time market data."""
    global cumulative_volume
    data = json.loads(message)
    
    price = float(data.get('p', 0))
    volume = float(data.get('v', 0))
    bid_size = float(data.get('b', 0))
    ask_size = float(data.get('a', 0))

    # Update indicators
    cumulative_volume += volume
    momentum_window.append(price)
    order_book_depth.append(bid_size - ask_size)  # Positive = Buy pressure, Negative = Sell pressure

    # Compute signals
    is_trending = compute_momentum()
    is_buy_pressure = compute_order_book_imbalance()

    # Execute trading logic
    if cumulative_volume > VOLUME_THRESHOLD and is_trending and is_buy_pressure:
        place_order("buy", price)
        cumulative_volume = 0  # Reset after trade

def start_websocket():
    """Start real-time market data feed."""
    ws = websocket.WebSocketApp("wss://public.coindcx.com", on_message=on_message)
    ws.run_forever()

if __name__ == "__main__":
    asyncio.run(fetch_market_data())  # Fetch initial market data
    start_websocket()  # Start WebSocket stream
