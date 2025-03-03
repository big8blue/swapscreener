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
        response.raise_for_status()  # Ensure we get a valid response
        data = response.json().get("data", [])

        if not data:
            return pd.DataFrame()

        df = pd.DataFrame(data)[["instId", "last", "vol24h", "ts"]]
        df.columns = ["Symbol", "Price", "Volume", "Timestamp"]
        df = df.astype({"Price": float, "Volume": float})
        df["Timestamp"] = pd.to_datetime(df["Timestamp"], unit="ms")

        return df
    except requests.RequestException as e:
        st.error(f"Error fetching data: {e}")
        return pd.DataFrame()

# Convert UTC to IST
def convert_to_ist(utc_time):
    return (utc_time + timedelta(hours=5, minutes=30)).strftime("%I:%M:%S %p")

# Store previous volumes for 5-minute comparison
if "prev_volumes" not in st.session_state:
    st.session_state.prev_volumes = {}

if "last_update" not in st.session_state:
    st.session_state.last_update = datetime.utcnow()

def track_volume(df):
    """Check volume difference after 5 minutes instead of every second."""
    now = datetime.utcnow()
    time_diff = (now - st.session_state.last_update).total_seconds()

    if time_diff < 300:  # Only update every 5 minutes
        return df  # Return as is without checking volume trend

    filtered_data = []
    for _, row in df.iterrows():
        symbol, current_volume = row["Symbol"], row["Volume"]
        prev_volume = st.session_state.prev_volumes.get(symbol, current_volume)
        st.session_state.prev_volumes[symbol] = current_volume  # Store latest volume
        filtered_data.append((symbol, row["Price"], current_volume, row["Timestamp"]))

    st.session_state.last_update = now  # Update timestamp
    return pd.DataFrame(filtered_data, columns=["Symbol", "Price", "Volume", "Timestamp"])

# Live Updates Without Glitches
placeholder = st.empty()

while True:
    df = fetch_data()
    if not df.empty:
        df_filtered = track_volume(df)
        df_filtered["Timestamp (IST)"] = df_filtered["Timestamp"].apply(convert_to_ist)
        df_filtered.drop(columns=["Timestamp"], inplace=True)

        # Display Data
        with placeholder.container():
            st.dataframe(df_filtered, height=600)

    time.sleep(1)  # Refresh every 1 second
