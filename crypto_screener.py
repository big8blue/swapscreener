import streamlit as st
import pandas as pd
import requests
import time

# API URL for USDT futures
API_URL = "https://api.coindcx.com/exchange/v1/derivatives/futures/data/active_instruments?margin_currency_short_name[]=USDT"

def fetch_futures_data():
    """Fetches real-time futures data from CoinDCX API"""
    try:
        response = requests.get(API_URL)
        data = response.json()

        # Extract required fields, handling missing data
        futures_data = []
        for item in data:
            futures_data.append({
                "Pair": item.get("symbol", "N/A"),  # Ensure correct key name
                "LTP": item.get("last_price", "N/A"),
                "Updated Time": time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
            })

        return pd.DataFrame(futures_data)

    except Exception as e:
        st.error(f"Error fetching data: {e}")
        return pd.DataFrame()

# Streamlit App
st.title("🚀 Real-Time Crypto Futures Screener")

# Sidebar input for refresh interval
refresh_seconds = st.sidebar.slider("Refresh Interval (seconds)", 1, 30, 5)

# Display data
df = fetch_futures_data()
st.dataframe(df)

# Auto-refresh
time.sleep(refresh_seconds)
st.experimental_rerun()
