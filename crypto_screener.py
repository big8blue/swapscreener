import streamlit as st
import websocket
import json
import pandas as 
import requests
import pandas as pd
import time
from datetime import datetime, timedelta

# OKX API for Swap Futures
API_URL = "https://www.okx.com/api/v5/market/tickers?instType=SWAP"

# Set Page Configuration
st.set_page_config(page_title="Crypto Screener", layout="wide")

st.title("🚀 Real-Time Crypto Futures Screener")

# Sidebar Filters
st.sidebar.header("🔍 Filters")

# Volume Range Input (User can type values)
st.sidebar.subheader("📊 Volume Range (in Millions)")
col1, col2 = st.sidebar.columns(2)
min_volume_input = col1.number_input("Min Volume (M)", min_value=0.0, max_value=1000.0, value=0.5, step=0.1)
max_volume_input = col2.number_input("Max Volume (M)", min_value=0.0, max_value=1000.0, value=50.0, step=0.1)

# Slider for convenience
min_volume, max_volume = st.sidebar.slider(
    "Or use the slider below",
    min_value=0.0,
    max_value=1000.0,
    value=(min_volume_input, max_volume_input),
    step=0.1
)

# Refresh Rate
refresh_rate = st.sidebar.slider("Refresh Rate (Seconds)", 1, 10, 1)

# Caching API Calls (refreshes every X seconds)
@st.cache_data(ttl=refresh_rate)
def fetch_data():
    """Fetch all swap futures tickers from OKX API."""
    try:
        response = requests.get(API_URL)
        data = response.json().get("data", [])
        if not data:
            return pd.DataFrame()

        df = pd.DataFrame(data)
        df = df[["instId", "last", "vol24h", "ts"]]
        df.columns = ["Symbol", "Price", "Volume", "Timestamp"]
        df["Price"] = df["Price"].astype(float)
        df["Volume"] = df["Volume"].astype(float) / 1_000_000  # Convert to Millions (M)
        df["Timestamp"] = pd.to_datetime(df["Timestamp"], unit="ms")

        # Filter only USDT pairs
        df = df[df["Symbol"].str.endswith("-USDT-SWAP")]

        return df
    except Exception as e:
        st.error(f"Error fetching data: {e}")
        return pd.DataFrame()

# Convert UTC to IST
def convert_to_ist(utc_time):
    ist_time = utc_time + timedelta(hours=5, minutes=30)
    return ist_time.strftime("%I:%M:%S %p")

# Live Updates with Auto Refresh
placeholder = st.empty()

def update_data():
    df = fetch_data()
    if not df.empty:
        df["Updated Time (IST)"] = df["Timestamp"].apply(convert_to_ist)
        df = df.drop(columns=["Timestamp"])

        # Apply min & max volume filter
        df = df[(df["Volume"] >= min_volume) & (df["Volume"] <= max_volume)]

        # Convert Volume to readable format (M)
        df["Volume"] = df["Volume"].apply(lambda x: f"{x:.2f}M")

        # Display Data
        with placeholder.container():
            st.dataframe(df.sort_values(by="Price", ascending=False), height=600)

while True:
    update_data()
    time.sleep(refresh_rate)  # Refresh based on user input
import threading
import time
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

# Start WebSocket connection
def start_websocket():
    ws = websocket.WebSocketApp(
        "wss://api.coindcx.com/ws",
        on_message=on_message,
        on_error=on_error,
        on_close=on_close
    )
    ws.on_open = on_open
    ws.run_forever()

# Run WebSocket in a separate thread
ws_thread = threading.Thread(target=start_websocket, daemon=True)
ws_thread.start()

# Streamlit UI
st.title("📊 CoinDCX Futures Screener (WebSocket)")

st.sidebar.header("Settings")
refresh_time = st.sidebar.slider("Refresh Interval (seconds)", 1, 10, 3)

# **🔄 Fix: Ensure Data Appears by Creating Dummy Data First**
if not futures_data:
    futures_data = {
        "B-BTC_USDT": {"LTP": "Fetching...", "Last Updated": "Waiting..."},
        "B-ETH_USDT": {"LTP": "Fetching...", "Last Updated": "Waiting..."},
        "B-SOL_USDT": {"LTP": "Fetching...", "Last Updated": "Waiting..."},
    }

# **✅ UI Updates Correctly Now**
placeholder = st.empty()

while True:
    df = pd.DataFrame.from_dict(futures_data, orient="index").reset_index()
    df.columns = ["Symbol", "LTP", "Last Updated"]
    
    placeholder.dataframe(df)  # ✅ Ensures UI updates dynamically
    
    time.sleep(refresh_time)  # ✅ Keeps UI refreshing without blocking
