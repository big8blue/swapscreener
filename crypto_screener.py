import streamlit as st
import websocket
import json
import pandas as pd
import threading
from datetime import datetime

# Set Streamlit UI
st.set_page_config(page_title="CoinDCX Futures Screener", layout="wide")
st.title("📈 CoinDCX Futures Screener")
st.sidebar.header("Settings")

# User-defined refresh interval
refresh_time = st.sidebar.number_input("Set refresh time (seconds)", min_value=1, max_value=60, value=5, step=1)

# WebSocket URL
WS_URL = "wss://stream.coindcx.com/market_data"

# Initialize session state
if "df" not in st.session_state:
    st.session_state.df = pd.DataFrame(columns=["Futures Name", "Last Traded Price", "24h High", "24h Low", "24h Volume", "Change (%)", "Last Updated Time"])

# WebSocket message handler
def on_message(ws, message):
    try:
        data = json.loads(message)

        # Ensure the message contains market data
        if isinstance(data, list):
            new_data = []
            for item in data:
                if "s" in item and "b" in item:
                    futures_name = item["s"]
                    last_price = float(item["b"])
                    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

                    # Extract additional data if available
                    high_24h = float(item.get("h", 0))
                    low_24h = float(item.get("l", 0))
                    volume_24h = float(item.get("v", 0))
                    change_24h = float(item.get("c", 0))

                    new_data.append({
                        "Futures Name": futures_name,
                        "Last Traded Price": last_price,
                        "24h High": high_24h,
                        "24h Low": low_24h,
                        "24h Volume": volume_24h,
                        "Change (%)": change_24h,
                        "Last Updated Time": timestamp
                    })

            # Update session state
            if new_data:
                st.session_state.df = pd.DataFrame(new_data)

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

# Display DataFrame with automatic refresh
data_placeholder = st.empty()
while True:
    data_placeholder.dataframe(st.session_state.df, use_container_width=True)
    time.sleep(refresh_time)
