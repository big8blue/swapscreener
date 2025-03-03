import streamlit as st
import requests
import pandas as pd
import time
from datetime import datetime, timedelta

# OKX API for Swap Futures
API_URL = "https://www.okx.com/api/v5/market/tickers?instType=SWAP"

# Set Page Configuration
st.set_page_config(page_title="Crypto Screener", layout="wide")

st.title("🚀 Real-Time Crypto Futures Screener")

# Sidebar Filters
st.sidebar.header("🔍 Filters")
min_volume = st.sidebar.slider("Min Volume (24h)", min_value=0, max_value=100000000, value=500000, step=50000)
refresh_rate = st.sidebar.slider("Refresh Rate (Seconds)", 1, 10, 1)

# Caching API Calls (refreshes every X seconds)
@st.cache_data(ttl=refresh_rate)
def fetch_data():
    """Fetch all swap futures tickers from OKX API."""
    try:
        response = requests.get(API_URL)
        data = response.json().get("data", [])
        if not data:
            return pd.DataFrame()

        df = pd.DataFrame(data)
        df = df[["instId", "last", "vol24h", "ts"]]
        df.columns = ["Symbol", "Price", "Volume", "Timestamp"]
        df["Price"] = df["Price"].astype(float)
        df["Volume"] = df["Volume"].astype(float)
        df["Timestamp"] = pd.to_datetime(df["Timestamp"], unit="ms")

        # Filter only USDT pairs
        df = df[df["Symbol"].str.endswith("-USDT-SWAP")]

        return df
    except Exception as e:
        st.error(f"Error fetching data: {e}")
        return pd.DataFrame()

# Convert UTC to IST
def convert_to_ist(utc_time):
    ist_time = utc_time + timedelta(hours=5, minutes=30)
    return ist_time.strftime("%I:%M:%S %p")

# Live Updates with Auto Refresh
placeholder = st.empty()

def update_data():
    df = fetch_data()
    if not df.empty:
        df["Updated Time (IST)"] = df["Timestamp"].apply(convert_to_ist)
        df = df.drop(columns=["Timestamp"])
        df = df[df["Volume"] >= min_volume]  # Apply volume filter

        # Display Data
        with placeholder.container():
            st.dataframe(df.sort_values(by="Volume", ascending=False), height=600)

while True:
    update_data()
    time.sleep(refresh_rate)  # Refresh based on user input
