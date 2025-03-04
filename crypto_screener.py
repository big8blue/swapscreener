import json
import websocket
import threading

# CoinDCX WebSocket URL
WS_URL = "wss://stream.coindcx.com/ws/v1"

# User input for futures trading pair (e.g., JASMYUSDT)
TRADE_SYMBOL = input("Enter the futures trading pair (e.g., JASMYUSDT): ").strip().upper()

# Subscription message for futures ticker data
subscribe_message = {
    "channel": "ticker",
    "payload": {
        "symbols": [TRADE_SYMBOL]
    }
}

def on_message(ws, message):
    """Process and display live market data."""
    data = json.loads(message)
    
    if 'ticker' in data:
        ticker = data['ticker']
        symbol = ticker.get('symbol', TRADE_SYMBOL)
        last_price = ticker.get('last_price', "N/A")
        best_bid = ticker.get('best_bid', "N/A")
        best_ask = ticker.get('best_ask', "N/A")
        volume = ticker.get('volume', "N/A")

        # Display real-time futures data
        print("\n🔹 **Real-Time Futures Data** 🔹")
        print(f"📌 Symbol: {symbol}")
        print(f"📈 Last Price: ${last_price}")
        print(f"📊 Best Bid: ${best_bid} | Best Ask: ${best_ask}")
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
    """Start real-time market data stream."""
    ws = websocket.WebSocketApp(
        WS_URL,
        on_open=on_open,
        on_message=on_message,
        on_error=on_error,
        on_close=on_close
    )
    ws.run_forever()

# Run WebSocket in a separate thread to prevent blocking
if __name__ == "__main__":
    print(f"📡 Connecting to CoinDCX WebSocket for {TRADE_SYMBOL} futures...")
    thread = threading.Thread(target=start_websocket)
    thread.start()
