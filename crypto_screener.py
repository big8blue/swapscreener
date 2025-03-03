import streamlit as st
import requests
import pandas as pd
import time
from datetime import datetime, timedelta

# OKX API Endpoint
API_URL = "https://www.okx.com/api/v5/market/tickers?instType=SWAP"

# Set Page Configuration
st.set_page_config(page_title="Crypto Screener", layout="wide")
st.title("🚀 Real-Time Crypto Futures Screener with Signals")

# Store historical data
if "historical_data" not in st.session_state:
    st.session_state.historical_data = {}

@st.cache_data(ttl=2)
def fetch_data():
    """Fetch live futures data from OKX API."""
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
    except Exception as e:
        st.error(f"Error fetching data: {e}")
        return pd.DataFrame()

def get_previous_data(symbol):
    """Fetch historical data from OKX API to compare with current values."""
    try:
        # Fetch historical data from OKX API (5 minutes ago)
        past_time = datetime.utcnow() - timedelta(minutes=5)
        past_timestamp = int(past_time.timestamp() * 1000)

        history_url = f"https://www.okx.com/api/v5/market/candles?instId={symbol}&bar=1m&limit=5"
        response = requests.get(history_url, timeout=5)
        response.raise_for_status()
        candles = response.json().get("data", [])

        if not candles or len(candles) < 5:
            return None  # Not enough data

    
