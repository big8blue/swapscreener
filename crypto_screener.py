import streamlit as st
import pandas as pd
import requests
import websocket
import json
import threading

# API URL for active futures
API_URL = "https://api.coindcx.com/exchange/v1/derivatives/futures/data/active_instruments"

# WebSocket URL
WEBSOCKET_URL = "wss://stream.coindcx.com"

# Streamlit Page Configuration
st.set_page_config(page_title="Crypto Screener", layout="wide")
st.title("🚀 Real-Time Crypto Futures Screener (WebSocket)")

st.sidebar.header("🔍 Filters")
refresh_rate = st.sidebar.slider("Refresh Rate (Seconds)", 1, 10, 1)

# Fetch all active futures instruments
@st.cache_data(ttl=refresh_rate)
def fetch_active_symbols():
    """Fetch active symbols only (since full instrument data is missing)."""
    try:
        response = requests.get(API_URL)
        data = response.json()

        if isinstance(data, list):
            symbols = [item["symbol"] for item in data if "symbol" in item]
            return pd.DataFrame(symbols, columns=["symbol"])
        else:
            st.error("Unexpected API response format")
            return None

    except Exception as e:
        st.error(f"Error fetching active instruments: {e}")
        return None

# Load active instruments
df = fetch_active_symbols()

# Dictionary to store real-time LTP data
ltp_data = {}

# WebSocket message handler
def on_message(ws, message):
    global ltp_data
    data = json.loads(message)
    for item in data.get("data", []):
        if "i" in item and "b" in item:
            ltp_data[item["i"]] = float(item["b"])  # Store LTP in dictionary

# WebSocket thread
def start_websocket():
    ws = websocket.WebSocketApp(
        WEBSOCKET_URL,
        on_message=on_message
    )
    ws.run_forever()

# Start WebSocket in a separate thread
ws_thread = threading.Thread(target=start_websocket, daemon=True)
ws_thread.start()

# Streamlit live update loop
if df is not None and not df.empty:
    while True:
        # Add LTP column from WebSocket updates
        df["LTP"] = df["symbol"].map(ltp_data)

        # Display table
        st.write("### Live Crypto Futures Screener")
        st.dataframe(df)

        # Refresh UI
        st.sleep(refresh_rate)
else:
    st.error("API did not return full instrument data. Fetching only symbols.")
