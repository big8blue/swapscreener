import streamlit as st
import requests
import pandas as pd
import time
from datetime import datetime

# Fetch futures data from CoinDCX API
def fetch_futures_data():
    url = "https://api.coindcx.com/exchange/v1/derivatives/futures/data/active_instruments?margin_currency_short_name[]=USDT"
    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()
        futures_list = []

        for item in data:
            futures_list.append({
                "Pair": item.get("symbol", "N/A"),  # Ensure correct key name
                "LTP": item.get("last_price", "N/A"),  # Last traded price
                "Updated Time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            })

        return pd.DataFrame(futures_list)
    else:
        st.error("⚠️ Failed to fetch futures data")
        return pd.DataFrame()

# Streamlit UI
st.set_page_config(page_title="CoinDCX Futures Screener", layout="wide")

# Sidebar Inputs
st.sidebar.header("⚙️ Settings")
refresh_seconds = st.sidebar.slider("⏳ Refresh Interval (seconds)", 1, 60, 5)  # User selects refresh rate

st.title("📊 CoinDCX Futures Screener")
st.write("Live futures data from CoinDCX with real-time updates.")

# Live Updates
while True:
    df = fetch_futures_data()
    
    if not df.empty:
        st.dataframe(df, height=600, width=800)  # Display table

    time.sleep(refresh_seconds)  # Refresh every X seconds
    st.experimental_rerun()  # Rerun script for updates
