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

# Track Volume Trends (Every 5 Minutes)
if "prev_volumes" not in st.session_state:
    st.session_state.prev_volumes = {}
if "last_trend_update" not in st.session_state:
    st.session_state.last_trend_update = datetime.utcnow()

def track_volume(df):
    """Filter tickers with a consistent increase or decrease in volume every 5 minutes."""
    filtered_data = []
    current_time = datetime.utcnow()

    for _, row in df.iterrows():
        symbol = row["Symbol"]
        current_volume = row["Volume"]

        if symbol in st.session_state.prev_volumes:
            prev_volume, last_update_time, trend = st.session_state.prev_volumes[symbol]

            # Update trend only if 5 minutes have passed
            if (current_time - last_update_time).total_seconds() >= 300:
                if current_volume > prev_volume:
                    trend = "🔼 Increasing"
                elif current_volume < prev_volume:
                    trend = "🔽 Decreasing"
                else:
                    trend = "➡ Stable"

                # Store the new volume and update time
                st.session_state.prev_volumes[symbol] = (current_volume, current_time, trend)
        else:
            trend = "🆕 New"
            st.session_state.prev_volumes[symbol] = (current_volume, current_time, trend)

        filtered_data.append((symbol, row["Price"], current_volume, trend, row["Timestamp"]))

    df_filtered = pd.DataFrame(filtered_data, columns=["Symbol", "Price", "Volume", "Trend", "Timestamp"])
    return df_filtered

# Convert UTC to IST
def convert_to_ist(utc_time):
    ist_time = utc_time + timedelta(hours=5, minutes=30)
    return ist_time.strftime("%I:%M:%S %p")

# Live Updates Without Glitches
placeholder = st.empty()

while True:
    df = fetch_data()
    if not df.empty:
        df_filtered = track_volume(df)
        df_filtered["Timestamp (IST)"] = df_filtered["Timestamp"].apply(convert_to_ist)
        df_filtered = df_filtered.drop(columns=["Timestamp"])

        # Display Data
        with placeholder.container():
            st.dataframe(df_filtered, height=600)

    time.sleep(1)  # Refresh every 1 second
