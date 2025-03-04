import streamlit as st
import websocket
import json
import pandas as pd
from datetime import datetime

# Global variables
futures_data = {}

# Function to process WebSocket messages
def on_message(ws, message):
    global futures_data
    data = json.loads(message)
    
    for item in data:
        market = item.get("s", "Unknown")
        price = item.get("bp", None)  # Best price (Last Traded Price)
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        if price:
            futures_data[market] = {"LTP": price, "Last Updated": timestamp}

# Function to handle errors
def on_error(ws, error):
    st.error(f"WebSocket Error: {error}")

# Function to handle WebSocket close
def on_close(ws, close_status_code, close_msg):
    st.warning("WebSocket Disconnected")

# Function to initiate WebSocket connection
def on_open(ws):
    st.success("Connected to CoinDCX WebSocket")
    
    # Subscribe to futures tickers
    subscription_payload = {
        "action": "subscribe",
        "channel": "market_data",
        "symbols": ["B-PONKE_USDT", "B-COW_USDT", "B-CETUS_USDT"]  # Modify based on available tickers
    }
    
    ws.send(json.dumps(subscription_payload))

# Streamlit UI
st.title("📈 Real-Time CoinDCX Futures Screener")

st.sidebar.header("Settings")
refresh_time = st.sidebar.slider("Refresh Interval (seconds)", 1, 10, 3)

# Start WebSocket
ws = websocket.WebSocketApp(
    "wss://api.coindcx.com/ws",
    on_message=on_message,
    on_error=on_error,
    on_close=on_close
)

ws.on_open = on_open

# Start WebSocket in the background
import threading
ws_thread = threading.Thread(target=ws.run_forever)
ws_thread.daemon = True
ws_thread.start()

# Main display loop
while True:
    if futures_data:
        df = pd.DataFrame.from_dict(futures_data, orient="index").reset_index()
        df.columns = ["Symbol", "LTP", "Last Updated"]
        st.dataframe(df)

    st.sleep(refresh_time)
