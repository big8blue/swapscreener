import streamlit as st
import pandas as pd
import requests
import time
import os
from dotenv import load_dotenv
from datetime import datetime

# Load API Keys from .env
load_dotenv()
API_KEY = os.getenv("COINDCX_API_KEY")
API_SECRET = os.getenv("COINDCX_API_SECRET")

# API URL for Futures data
API_URL = "https://api.coindcx.com/exchange/v1/derivatives/futures/data/active_instruments?margin_currency_short_name[]=USDT"

# Streamlit App UI
st.set_page_config(page_title="Crypto Futures Screener", layout="wide")
st.title("🚀 Real-Time Crypto Futures Screener")

# Sidebar Settings
refresh_interval = st.sidebar.slider("⏳ Set Refresh Interval (Seconds)", 1, 30, 5)

# Function to fetch futures data
def fetch_futures_data():
    response = requests.get(API_URL)
    if response.status_code == 200:
        data = response.json()
        futures_data = []
        for item in data:
            futures_data.append({
                "Pair": item.get("contract_name", "N/A"),
                "LTP": item.get("last_price", "N/A"),
                "Updated Time": datetime.utcfromtimestamp(item.get("updated_at", 0)).strftime('%Y-%m-%d %H:%M:%S')
            })
        return pd.DataFrame(futures_data)
    else:
        st.error("❌ Failed to fetch data. API Error: " + str(response.status_code))
        return pd.DataFrame()

# Display Data in Table
while True:
    df = fetch_futures_data()
    if not df.empty:
        st.dataframe(df)
    else:
        st.warning("⚠️ No data available.")
    
    # Auto-refresh
    time.sleep(refresh_interval)
    st.experimental_rerun()
