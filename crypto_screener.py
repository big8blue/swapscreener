import streamlit as st
import requests
import pandas as pd
import time

# CoinDCX API for all tickers
API_URL = "https://public.coindcx.com/exchange/ticker"

st.set_page_config(page_title="Crypto Futures Screener", layout="wide")
st.title("🚀 Real-Time Crypto Futures Screener (USDT Pairs)")

# Initialize session state for historical prices
if "prev_prices_5m" not in st.session_state:
    st.session_state.prev_prices_5m = {}
if "prev_prices_15m" not in st.session_state:
    st.session_state.prev_prices_15m = {}
if "timestamps_5m" not in st.session_state:
    st.session_state.timestamps_5m = {}
if "timestamps_15m" not in st.session_state:
    st.session_state.timestamps_15m = {}

@st.cache_data(ttl=5)  # Cache data for 5 seconds
def fetch_data():
    """Fetch all USDT pair tickers from CoinDCX API."""
    try:
        response = requests.get(API_URL)
        data = response.json()
        if not data:
            return pd.DataFrame()

        # Convert to DataFrame
        df = pd.DataFrame(data)

        # Filter for USDT pairs
        df = df[df["market"].str.endswith("USDT")]

        # Select relevant columns
