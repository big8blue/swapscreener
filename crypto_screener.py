import streamlit as st
import websocket
import json
import pandas as pd
import time
import requests
from datetime import datetime
import threading

# Streamlit UI settings
st.set_page_config(page_title="CoinDCX Futures Screener", layout="wide")

st.title("📈 CoinDCX Futures Screener")
st.sidebar.header("Settings")

# User-defined refresh interval
refresh_time = st.sidebar.number_input("Set refresh time (seconds)", min_value=1, max_value=60, value=5, step=1)

# WebSocket URL
WS_URL = "wss://stream.coindcx.com/socket.io/?EIO=3&transport=websocket"

# Initialize session state for DataFrame
if "df" not in st.session_state:
    st.session_state.df = pd.DataFrame(columns=["Futures Name", "Last Traded Price", "24h High", "24h Low", "24h Volume", "Change (%)", "Last Updated Time"])

# Fetch 24h market data from CoinDCX REST API
def fetch_24h_data():
    url = "https://api.coindcx.com/exchange/ticker"
    try:
        response = requests.get(url)
        data = response.json()
        return {item["market"]: item for item in data}
    except:
        return {}

# WebSocket message handler
def on_message(ws, message):
    try:
        data = json.loads(message)
        market_data = fetch_24h_data()

        if isinstance(data, list):
            for item in data:
                if "m" in item and "b" in item and "s" in item:
                    futures_name = item["s"]
                    last_price = float(item["b"])
                    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

                    # Get additional data
                    market_info = market_data.get(futures_name, {})
                    high_24h = float(market_info.get("high", 0))
                    low_24h = float(market_info.get("low", 0))
                    volume_24h = float(market_info.get("volume", 0))
                    change_24h = float(market_info.get("change_24_hour", 0))

                    new_row = {
                        "Futures Name": futures_name,
                        "Last Traded Price": last_price,
                        "24h High": high_24h,
                        "24h Low": low_24h,
                        "24h Volume": volume_24h,
                        "Change (%)": change_24h,
                        "Last Updated Time": timestamp
                    }

                    # Update session state
                    st.session_state.df = pd.concat([st.session_state.df, pd.DataFrame([new_row])], ignore_index=True).drop_duplicates(subset=["Futures Name"], keep="last")

    except json.JSONDecodeError:
        pass

# WebSocket connection
def connect_websocket():
    ws = websocket.WebSocketApp(WS_URL, on_message=on_message)
    ws.run_forever()

# Run WebSocket in the background
ws_thread = threading.Thread(target=connect_websocket, daemon=True)
ws_thread.start()

# Streamlit UI update loop
table_placeholder = st.empty()

while True:
    table_placeholder.dataframe(st.session_state.df, use_container_width=True)
    time.sleep(refresh_time)
