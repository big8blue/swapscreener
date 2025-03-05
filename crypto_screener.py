import streamlit as st
import pandas as pd
import requests
import websocket
import json
import threading

# API URLs
API_URL = "https://api.coindcx.com/exchange/v1/derivatives/futures/data/active_instruments"
WEBSOCKET_URL = "wss://stream.coindcx.com"

# Streamlit Page Configuration
st.set_page_config(page_title="Crypto Screener", layout="wide")
st.title("🚀 Real-Time Crypto Futures Screener (WebSocket)")

st.sidebar.header("🔍 Filters")
refresh_rate = st.sidebar.slider("Refresh Rate (Seconds)", 1, 10, 1)

# Fetch all active futures instruments
@st.cache_data(ttl=refresh_rate)
def fetch_active_instruments():
    try:
        response = requests.get(API_URL)
        data = response.json()
        
        if isinstance(data, list):
            df = pd.DataFrame(data)
            st.write("### Debug: API Response Sample", df.head())  # Print sample data
            return df
        else:
            st.error("Unexpected API response format")
            return None

    except Exception as e:
        st.error(f"Error fetching active instruments: {e}")
        return None

# Load active instruments
df = fetch_active_instruments()

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
if df is not None:
    available_columns = df.columns.tolist()
    st.write("### Debug: Available Columns in API Response", available_columns)

    # Extract only available columns
    expected_columns = ["symbol", "mark_price", "volume", "timestamp"]
    valid_columns = [col for col in expected_columns if col in available_columns]

    if valid_columns:
        df_filtered = df[valid_columns]

        # Convert timestamp
        if "timestamp" in df_filtered.columns:
            df_filtered["timestamp"] = pd.to_datetime(df_filtered["timestamp"], unit='ms')

        while True:
            # Add LTP column from WebSocket updates
            df_filtered["ltp"] = df_filtered["symbol"].map(ltp_data)

            # Display table
            st.write("### Live Crypto Futures Screener")
            st.dataframe(df_filtered)

            # Refresh UI
            st.sleep(refresh_rate)
    else:
        st.error("API returned only symbols, not full instrument data.")
