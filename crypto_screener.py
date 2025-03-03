import streamlit as st
import requests
import pandas as pd
import time
from datetime import datetime, timedelta

# OKX API for swap futures
API_URL = "https://www.okx.com/api/v5/market/tickers?instType=SWAP"

# Set Page Configuration
st.set_page_config(page_title="Crypto Screener", layout="wide")

st.title("🚀 Real-Time Crypto Futures Screener")

# Caching API Calls (refreshes every 1 second)
@st.cache_data(ttl=1)
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

        return df
    except Exception as e:
        st.error(f"Error fetching data: {e}")
        return pd.DataFrame()

# Convert UTC to IST
def convert_to_ist(utc_time):
    ist_time = utc_time + timedelta(hours=5, minutes=30)
    return ist_time.strftime("%I:%M:%S %p")

# Sidebar for Filters
st.sidebar.header("🔍 Filters")
min_volume = st.sidebar.number_input("Min Volume (24h)", value=500000, step=100000)
refresh_rate = st.sidebar.slider("Refresh Rate (Seconds)", 1, 10, 1)

# Live Updates with Auto Refresh
placeholder = st.empty()

while True:
    df = fetch_data()
    if not df.empty:
        df["Updated Time (IST)"] = df["Timestamp"].apply(convert_to_ist)
        df = df.drop(columns=["Timestamp"])
        df = df[df["Volume"] >= min_volume]  # Apply volume filter

        # Display Data
        with placeholder.container():
            st.dataframe(df.sort_values(by="Volume", ascending=False), height=600)

    time.sleep(refresh_rate)  # Refresh based on user input



