import streamlit as st
import websocket
import json
import pandas as pd
import threading
from datetime import datetime

# Streamlit UI setup
st.set_page_config(page_title="CoinDCX Futures Screener", layout="wide")
st.title("📈 CoinDCX Real-Time Futures List")

# WebSocket URL
WS_URL = "wss://stream.coindcx.com/market_data"

# Initialize session state
if "futures_data" not in st.session_state:
    st.session_state.futures_data = pd.DataFrame(columns=["Futures Name", "Last Traded Price", "Last Updated Time"])

# WebSocket message handler
def on_message(ws, message):
    try:
        data = json.loads(message)
        new_data = []
        
        for item in data:
            if "s" in item and "b" in item:
                futures_name = item["s"]
                last_price = float(item["b"])
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

                new_data.append({"Futures Name": futures_name, "Last Traded Price": last_price, "Last Updated Time": timestamp})

        if new_data:
            st.session_state.futures_data = pd.DataFrame(new_data)

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
st.dataframe(st.session_state.futures_data, use_container_width=True)
