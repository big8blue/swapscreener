import streamlit as st
import websocket
import json
import pandas as pd
import time
import threading
from datetime import datetime

# Global dictionary to store futures data
futures_data = {}

# WebSocket message handler
def on_message(ws, message):
    global futures_data
    data = json.loads(message)
    
    for item in data:
        market = item.get("s", "Unknown")
        price = item.get("bp", None)  # Best price (LTP)
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        if price:
            futures_data[market] = {"LTP": price, "Last Updated": timestamp}

# WebSocket error handler
def on_error(ws, error):
    st.error(f"WebSocket Error: {error}")

# WebSocket close handler
def on_close(ws, close_status_code, close_msg):
    st.warning("WebSocket Disconnected")

# WebSocket open handler
def on_open(ws):
    st.success("Connected to CoinDCX WebSocket")
    
    # Subscribe to market data
    subscription_payload = {
        "action": "subscribe",
        "channel": "market_data",
        "symbols": ["B-BTC_USDT", "B-ETH_USDT", "B-SOL_USDT"]  # Modify based on available futures
    }
    
    ws.send(json.dumps(subscription_payload))

# Start WebSocket
ws = websocket.WebSocketApp(
    "wss://api.coindcx.com/ws",
    on_message=on_message,
    on_error=on_error,
    on_close=on_close
)

ws.on_open = on_open

# Run WebSocket in a separate thread
ws_thread = threading.Thread(target=ws.run_forever)
ws_thread.daemon = True
ws_thread.start()

# Streamlit UI
st.title("📈 CoinDCX Real-Time Futures Screener")

st.sidebar.header("Settings")
refresh_time = st.sidebar.slider("Refresh Interval (seconds)", 1, 10, 3)

# **🔄 Fix: Use `st.empty()` to update UI dynamically**
placeholder = st.empty()

while True:
    if futures_data:
        df = pd.DataFrame.from_dict(futures_data, orient="index").reset_index()
        df.columns = ["Symbol", "LTP", "Last Updated"]
        
        placeholder.dataframe(df)  # ✅ UI updates dynamically
    
    time.sleep(refresh_time)  # ✅ UI does not freeze
