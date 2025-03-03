import streamlit as st
import requests
import pandas as pd
import time
from datetime import datetime, timedelta

# OKX API for all swap tickers
API_URL = "https://www.okx.com/api/v5/market/tickers?instType=SWAP"

# Set Page Configuration
st.set_page_config(page_title="Crypto Screener", layout="wide")
st.title("🚀 Real-Time Crypto Futures Screener with Signals")

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

# Store previous data only every 5 minutes
if "historical_data" not in st.session_state:
    st.session_state.historical_data = {}

def generate_signal(df):
    """Generate buy/sell/neutral signals based on price and volume changes over 5 minutes."""
    signals = []
    current_time = datetime.utcnow()

    for _, row in df.iterrows():
        symbol = row["Symbol"]
        current_price = row["Price"]
        current_volume = row["Volume"]

        # Check if we have past data stored
        if symbol in st.session_state.historical_data:
            prev_entry = st.session_state.historical_data[symbol]
            prev_time = prev_entry["Timestamp"]

            # Ensure at least 5 minutes have passed
            if (current_time - prev_time).total_seconds() >= 300:
                prev_price = prev_entry["Price"]
                prev_volume = prev_entry["Volume"]

                # Calculate % change
                price_change = ((current_price - prev_price) / prev_price) * 100
                volume_change = ((current_volume - prev_volume) / prev_volume) * 100

                # Define thresholds
                price_threshold = 1.0  # 1% price change
                volume_threshold = 5.0  # 5% volume change

                if price_change > price_threshold and volume_change > volume_threshold:
                    signal = "BUY 📈"
                elif price_change < -price_threshold and volume_change > volume_threshold:
                    signal = "SELL 📉"
                else:
                    signal = "NEUTRAL ⚖"

                # Update stored data every 5 minutes
                st.session_state.historical_data[symbol] = {
                    "Price": current_price,
                    "Volume": current_volume,
                    "Timestamp": current_time,
                }
            else:
                signal = "WAIT ⏳"  # Still waiting for 5-minute difference
        else:
            # First time storing data for this symbol
            st.session_state.historical_data[symbol] = {
                "Price": current_price,
                "Volume": current_volume,
                "Timestamp": current_time,
            }
            signal = "WAIT ⏳"  # No historical data yet

        signals.append((symbol, current_price, current_volume, signal))

    return pd.DataFrame(signals, columns=["Symbol", "Price", "Volume", "Signal"])

# Live Updates Without Glitches
placeholder = st.empty()

while True:
    df = fetch_data()
    if not df.empty:
        df_signals = generate_signal(df)

        # Display Data
        with placeholder.container():
            st.dataframe(df_signals, height=600)

    time.sleep(1)  # Refresh every 1 second
