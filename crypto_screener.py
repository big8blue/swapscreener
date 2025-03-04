import streamlit as st
import websocket
import json
import pandas as pd
import threading
import requests
from datetime import datetime

# Streamlit UI setup
st.set_page_config(page_title="JASMY Futures Screener", layout="wide")
st.title("📈 JASMY Futures Screener (Real-Time)")

# WebSocket URL
WS_URL = "wss://stream.coindcx.com/market_data"
REST_API_URL = "https://api.coindcx.com/exchange/v1/derivatives/futures/data/active_instruments?margin_currency_short_name[]=USDT"

# Initialize session state
if "jasmy_data" not in st.session_state:
    st.session_state.jasmy_data = pd.DataFrame(columns=["Futures Name", "Last Traded Price", "24h High", "24h Low", "24h Volume", "Change (%)", "Last Updated Time"])

# Fetch 24h market data from REST API
def fetch_24h_data():
    try:
        response = requests.get(REST_API_URL)
        data = response.json()
        return {item["market"]: item for item in data if "JASMY" in item["market"]}
    except:
        return {}

# WebSocket message handler
def on_message(ws, message):
    try:
        data = json.loads(message)
        market_data = fetch_24h_data()  # Fetch latest 24h data

        new_data = []
        for item in data:
            if "s" in item and "b" in item and "JASMY" in item["s"]:  # Filter JASMY futures
                futures_name = item["s"]
                last_price = float(item["b"])
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

                # Fetch 24h data from API
                market_info = market_data.get(futures_name, {})
                high_24h = float(market_info.get("high", 0))
                low_24h = float(market_info.get("low", 0))
                volume_24h = float(market_info.get("volume", 0))
                change_24h = float(market_info.get("change_24_hour", 0))

                new_data.append({
                    "Futures Name": futures_name,
                    "Last Traded Price": last_price,
                    "24h High": high_24h,
                    "24h Low": low_24h,
                    "24h Volume": volume_24h,
                    "Change (%)": change_24h,
                    "Last Updated Time": timestamp
                })

        if new_data:
            st.session_state.jasmy_data = pd.DataFrame(new_data)

    except json.JSONDecodeError:
        pass

# WebSocket connection
def connect_websocket():
    ws = websocket.WebSocketApp(WS_URL, on_message=on_message)
    ws.run_forever()

# Start WebSocket in a background thread
if "websocket_thread" not in st.session_state:
    ws_thread = threading.Thread(target=connect_websocket, daemon=True)
    ws_thread.start()
    st.session_state.websocket_thread = ws_thread

# Display DataFrame with auto-refresh
st.dataframe(st.session_state.jasmy_data, use_container_width=True)
