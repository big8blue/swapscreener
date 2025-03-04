import json
import websocket

# User input for futures trading pair (e.g., JASMYUSDT)
TRADE_SYMBOL = input("Enter the futures trading pair (e.g., JASMYUSDT): ").strip().upper()

# CoinDCX WebSocket URL
WS_URL = "wss://stream.coindcx.com/ws/v1"

# Subscription message for futures data
subscribe_message = {
    "channel": "ticker",
    "payload": {
        "symbol": TRADE_SYMBOL
    }
}

def on_message(ws, message):
    """Handle incoming WebSocket messages and display live market data."""
    data = json.loads(message)
    
    if 'ticker' in data:
        ticker = data['ticker']
        price = float(ticker.get('last_price', 0))
        bid_price = float(ticker.get('best_bid', 0))
        ask_price = float(ticker.get('best_ask', 0))
        volume = float(ticker.get('volume', 0))

        # Display real-time futures data
        print(f"\n🔹 **{TRADE_SYMBOL} Futures Data** 🔹")
        print(f"📌 Current Price: ${price}")
        print(f"📈 Best Bid: ${bid_price}  |  📉 Best Ask: ${ask_price}")
        print(f"💰 24h Volume: {volume}")
        print("-" * 40)

def on_open(ws):
    """Send subscription message once the WebSocket connection opens."""
    ws.send(json.dumps(subscribe_message))
    print(f"📡 Connected! Listening for {TRADE_SYMBOL} futures data...")

def on_error(ws, error):
    """Handle WebSocket errors."""
    print(f"❌ WebSocket Error: {error}")

def on_close(ws, close_status, close_message):
    """Handle WebSocket closing."""
    print("🔴 WebSocket Disconnected.")

def start_websocket():
    """Start real-time market data feed."""
    ws = websocket.WebSocketApp(
        WS_URL,
        on_open=on_open,
        on_message=on_message,
        on_error=on_error,
        on_close=on_close
    )
    ws.run_forever()

if __name__ == "__main__":
    print(f"📡 Connecting to CoinDCX WebSocket for {TRADE_SYMBOL} futures...")
    start_websocket()
