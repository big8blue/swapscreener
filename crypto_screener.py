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

# Store Historical Data for 5-Minute Analysis
if "historical_data" not in st.session_state:
    st.session_state.historical_data = {}

def get_previous_data(symbol):
    """Retrieve stored historical data for a given symbol."""
    if symbol in st.session_state.historical_data:
        prev_entry = st.session_state.historical_data[symbol]
        return prev_entry["Price"], prev_entry["Volume"]
    return None

def update_historical_data(df):
    """Update historical data for analysis (without signal generation)."""
    current_time = datetime.utcnow()
    for _, row in df.iterrows():
        symbol = row["Symbol"]
        current_price = row["Price"]
        current_volume = row["Volume"]

        # Store new data
        st.session_state.historical_data[symbol] = {
            "Price": current_price,
            "Volume": current_volume,
            "Timestamp": current_time
        }

# Convert UTC to IST
def convert_to_ist(utc_time):
    ist_time = utc_time + timedelta(hours=5, minutes=30)
    return ist_time.strftime("%I:%M:%S %p")

# Live Updates Without Glitches
placeholder = st.empty()

while True:
    df = fetch_data()
    if not df.empty:
        update_historical_data(df)
        df["Updated Time (IST)"] = df["Timestamp"].apply(convert_to_ist)
        df = df.drop(columns=["Timestamp"])

        # Display Data
        with placeholder.container():
            st.dataframe(df, height=600)

    time.sleep(1)  # Refresh every 1 second
