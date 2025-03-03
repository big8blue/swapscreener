import streamlit as st
import requests
import pandas as pd
import time
from datetime import datetime, timedelta

# OKX API for all swap tickers
API_URL = "https://www.okx.com/api/v5/market/tickers?instType=SWAP"

# Set Page Configuration
st.set_page_config(page_title="Crypto Screener", layout="wide")
st.title("🚀 Real-Time Crypto Futures Screener")

# Caching API Calls (refreshes every 2 seconds)
@st.cache_data(ttl=2)
def fetch_data():
    """Fetch all swap futures tickers from OKX API."""
    try:
        response = requests.get(API_URL, timeout=5)
        response.raise_for_status()
        data = response.json().get("data", [])
        if not data:
            return pd.DataFrame()

        df = pd.DataFrame(data)[["instId", "last", "vol24h", "ts"]]
        df.columns = ["Symbol", "Price", "Volume", "Timestamp"]
        df["Price"] = df["Price"].astype(float)
        df["Volume"] = df["Volume"].astype(float)
        df["Timestamp"] = pd.to_datetime(df["Timestamp"], unit="ms")

        return df
    except:
        return pd.DataFrame()

# Convert UTC to IST
def convert_to_ist(utc_time):
    return (utc_time + timedelta(hours=5, minutes=30)).strftime("%I:%M:%S %p")

# Live Updates Without Glitches
placeholder = st.empty()

while True:
    df = fetch_data()
    if not df.empty:
        df["Timestamp (IST)"] = df["Timestamp"].apply(convert_to_ist)
        df.drop(columns=["Timestamp"], inplace=True)

        # Display Data
        with placeholder.container():
            st.dataframe(df, height=600)

    time.sleep(1)  # Refresh every 1 second
