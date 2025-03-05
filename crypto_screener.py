import streamlit as st
import websocket
import json
import pandas as pd
import threading
import time

# Streamlit UI Config
st.set_page_config(page_title="Crypto Futures Screener", layout="wide")
st.title("🚀 Real-Time Crypto Futures Screener (WebSocket)")

# Sidebar Settings
st.sidebar.header("🔍 Filters")
refresh_rate = st.sidebar.slider("Refresh Rate (Seconds)", 1, 10, 1)

# WebSocket Endpoint
WEBSOCKET_URL = "wss://api.coindcx.com/streaming"

# Shared data storage
latest_data = {}

# WebSocket Connection
def on_message(ws, message):
    """Handles incoming WebSocket messages."""
    global latest_data
    try:
        response = json.loads(message)
        if "data" in response:
            for update in response["data"]:
                symbol = update.get("i", "Unknown")  # Instrument Symbol
                last_price = update.get("p", None)  # Last Traded Price
                best_bid = update.get("b", None)    # Best Bid Price
                best_ask = update.get("a", None)    # Best Ask Price
                timestamp = update.get("t", None)   # Timestamp
                
                latest_data[symbol] = {
                    "Symbol": symbol,
                    "LTP": last_price,
                    "Best Bid": best_bid,
                    "Best Ask": best_ask,
                    "Timestamp": pd.to_datetime(timestamp, unit="ms") if timestamp else None
                }
    except Exception as e:
        st.error(f"Error processing WebSocket message: {e}")

def on_error(ws, error):
    """Handles WebSocket errors."""
    st.error(f"WebSocket Error: {error}")

def on_close(ws, close_status_code, close_msg):
    """Handles WebSocket closure."""
    st.warning("WebSocket connection closed. Reconnecting in 5 seconds...")
    time.sleep(5)
    start_websocket()  # Auto-reconnect

def on_open(ws):
    """Subscribes to futures data on WebSocket connection."""
    subscribe_msg = {
        "channel": "subscribe",
        "streams": ["currentPrices@futures#update"]
    }
    ws.send(json.dumps(subscribe_msg))

def start_websocket():
    """Starts the WebSocket connection."""
    ws = websocket.WebSocketApp(
        WEBSOCKET_URL,
        on_message=on_message,
        on_error=on_error,
        on_close=on_close,
        on_open=on_open
    )
    ws.run_forever()

# Run WebSocket in a separate thread
ws_thread = threading.Thread(target=start_websocket, daemon=True)
ws_thread.start()

# Main Streamlit UI loop
while True:
    if latest_data:
        df = pd.DataFrame(list(latest_data.values()))

        # Display in Streamlit
        st.write("### Live Futures Data")
        st.dataframe(df, height=600)

    time.sleep(refresh_rate)  # Refresh at user-defined interval
