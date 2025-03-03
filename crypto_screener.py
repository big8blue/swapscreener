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

# Fetch 5-minute historical data for price & volume comparison
def get_previous_data(symbol):
    """Fetch historical data from OKX API to compare with current values."""
    try:
        history_url = f"https://www.okx.com/api/v5/market/candles?instId={symbol}&bar=1m&limit=5"
        response = requests.get(history_url, timeout=5)
        response.raise_for_status()
        candles = response.json().get("data", [])

        if not candles or len(candles) < 5:
            return None  # Not enough data

        # Use the oldest candle (5 min ago)
        prev_close = float(candles[-1][4])  # Closing price 5 min ago
        prev_volume = float(candles[-1][5])  # Volume 5 min ago

        return prev_close, prev_volume
    except Exception as e:
        st.warning(f"Error fetching historical data for {symbol}: {e}")
        return None

# Generate Buy/Sell/Neutral signals
def generate_signal(df):
    """Generate buy/sell/neutral signals based on price and volume changes over 5 minutes."""
    signals = []
    current_time = datetime.utcnow()

    for _, row in df.iterrows():
        symbol = row["Symbol"]
        current_price = row["Price"]
        current_volume = row["Volume"]
        current_timestamp = row["Timestamp"]

        # Fetch past data from API
        historical_data = get_previous_data(symbol)
        if historical_data:
            prev_price, prev_volume = historical_data

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
        else:
            signal = "WAIT ⏳"  # Not enough historical data

        signals.append((symbol, current_price, current_volume, signal, current_timestamp))

    return pd.DataFrame(signals, columns=["Symbol", "Price", "Volume", "Signal", "Updated Time"])

# Convert UTC to IST
def convert_to_ist(utc_time):
    ist_time = utc_time + timedelta(hours=5, minutes=30)
    return ist_time.strftime("%I:%M:%S %p")

# Live Updates Without Glitches
placeholder = st.empty()

while True:
    df = fetch_data()
    if not df.empty:
        df_signals = generate_signal(df)
        df_signals["Updated Time (IST)"] = df_signals["Updated Time"].apply(convert_to_ist)
        df_signals = df_signals.drop(columns=["Updated Time"])

        # Display Data
        with placeholder.container():
            st.dataframe(df_signals, height=600)

    time.sleep(1)  # Refresh every 1 second
