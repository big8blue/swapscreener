import streamlit as st
import pandas as pd
import requests
import time

# API URL for USDT futures
API_URL = "https://api.coindcx.com/exchange/v1/derivatives/futures/data/active_instruments?margin_currency_short_name[]=USDT"

def fetch_futures_data():
    """Fetches real-time futures data from CoinDCX API and handles errors."""
    try:
        response = requests.get(API_URL)

        # Check if response is valid JSON
        if response.status_code != 200:
            st.error(f"API Error: {response.status_code}")
            return pd.DataFrame()

        data = response.json()

        # Check if API response is a list (expected format)
        if not isinstance(data, list):
            st.error("Unexpected API response format!")
            return pd.DataFrame()

        # Extract required fields, handling missing data
        futures_data = []
        for item in data:
            if isinstance(item, dict):  # Ensure item is a dictionary
                futures_data.append({
                    "Pair": item.get("symbol", "N/A"),  # Correct key name
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

# Fetch and display data
df = fetch_futures_data()
if not df.empty:
    st.dataframe(df)
else:
    st.warning("No data available. Check API or try again later.")

# Auto-refresh
time.sleep(refresh_seconds)
st.experimental_rerun()
