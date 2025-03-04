import asyncio
import json
import aiohttp
import websocket
import requests
import numpy as np
import hmac
import hashlib
import time
from collections import deque
import os

# Load API keys securely
API_KEY = os.getenv("COINDCX_API_KEY")
SECRET_KEY = os.getenv("COINDCX_SECRET_KEY")

if not API_KEY or not SECRET_KEY:
    raise ValueError("API keys missing! Set them as environment variables.")

# Get user inputs
TRADE_SYMBOL = input("Enter the trading pair (e.g., JASMYUSDT): ").strip().upper()
LEVERAGE = int(input("Enter leverage (e.g., 10 for 10x): "))

# API & WebSocket URLs
BASE_URL = "https://api.coindcx.com"
WS_URL = "wss://stream.coindcx.com"

# HFT Strategy Parameters
MIN_TRADE_SIZE_USD = 6.05  
VOLUME_THRESHOLD = 50000  
momentum_window = deque(maxlen=5)
order_book_depth = deque(maxlen=5)
cumulative_volume = 0

async def fetch_market_price():
    """Fetch the latest market price."""
    url = f"{BASE_URL}/market_data"
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            data = await response.json()
            return float(data[TRADE_SYMBOL]['last_price'])

def get_trade_quantity(price):
    """Calculate trade quantity based on min trade size."""
    return round(MIN_TRADE_SIZE_USD / price, 4)  

def compute_momentum():
    """Detect market trend direction."""
    if len(momentum_window) < 5:
        return None
    diff = np.diff(momentum_window)
    return np.all(diff > 0) or np.all(diff < 0)

def compute_order_book_imbalance():
    """Determine bid/ask imbalance."""
    if len(order_book_depth) < 5:
        return None
    avg_imbalance = np.mean(order_book_depth)
    return avg_imbalance > 0  

def create_order_payload(order_type, price):
    """Create order payload with signature."""
    quantity = get_trade_quantity(price) * LEVERAGE
    timestamp = int(time.time() * 1000)
    payload = {
        "symbol": TRADE_SYMBOL,
        "side": order_type,
        "quantity": quantity,
        "order_type": "market",
        "timestamp": timestamp
    }
    
    payload_json = json.dumps(payload, separators=(',', ':'))
    signature = hmac.new(SECRET_KEY.encode(), payload_json.encode(), hashlib.sha256).hexdigest()
    
    return payload, signature

def place_order(order_type, price):
    """Execute trade on CoinDCX."""
    payload, signature = create_order_payload(order_type, price)
    headers = {
        "X-AUTH-APIKEY": API_KEY,
        "X-AUTH-SIGNATURE": signature,
        "Content-Type": "application/json"
    }
    
    response = requests.post(f"{BASE_URL}/trade", json=payload, headers=headers)
    if response.status_code == 200:
        print(f"✅ {order_type.upper()} order placed: {TRADE_SYMBOL} at {price} with {LEVERAGE}x leverage")
    else:
        print(f"❌ Order failed! Response: {response.text}")

def on_message(ws, message):
    """Handle real-time trade data."""
    global cumulative_volume
    data = json.loads(message)

    for trade in data.get('data', []):
        if trade['s'] == TRADE_SYMBOL:
            price = float(trade['p'])
            volume = float(trade['q'])
            bid_size = float(trade.get('b', 0))  
            ask_size = float(trade.get('a', 0))  

            # Update indicators
            cumulative_volume += volume
            momentum_window.append(price)
            order_book_depth.append(bid_size - ask_size)

            # Compute signals
            is_trending = compute_momentum()
            is_buy_pressure = compute_order_book_imbalance()

            # Execute trade logic
            if cumulative_volume > VOLUME_THRESHOLD and is_trending and is_buy_pressure:
                place_order("buy", price)
                cumulative_volume = 0  

def start_websocket():
    """Start WebSocket connection for live market data."""
    ws_payload = {
        "event": "subscribe",
        "streams": [f"{TRADE_SYMBOL}@trade"]
    }

    def on_open(ws):
        ws.send(json.dumps(ws_payload))

    ws = websocket.WebSocketApp(WS_URL, on_message=on_message, on_open=on_open)
    ws.run_forever()

if __name__ == "__main__":
    asyncio.run(fetch_market_price())
    start_websocket()
