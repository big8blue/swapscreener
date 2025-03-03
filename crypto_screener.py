import streamlit as st
import requests
import pandas as pd
from datetime import datetime, timedelta

# OKX API for all swap tickers
API_URL = "https://www.okx.com/api/v5/market/tickers?instType=SWAP"

# Set Page Configuration
st.set_page_config(page_title="Crypto Screener", layout="wide")

st.title("🚀 Real-Time Crypto Futures Screener")

# User-defined refresh interval
refresh_rate = st.sidebar.slider("Refresh rate (seconds)", 1, 10, 2)

# Fetch Data Function (Cached for 2 Seconds)
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

        return df
    except Exception as e:
        st.error(f"Error fetching data: {e}")
        return pd.DataFrame()

# Track Volume Trends
if "prev_volumes" not in st.session_state:
    st.session_state.prev_volumes = {}

def track_volume(df):
    """Filter tickers with a consistent increase or decrease in volume."""
    filtered_data = []
    for _, row in df.iterrows():
        symbol = row["Symbol"]
        current_volume = row["Volume"]

        prev_volume = st.session_state.prev_volumes.get(symbol, 0)
        if current_volume > prev_volume:
            trend = "🔼 Increasing"
        elif current_volume < prev_volume:
            trend = "🔽 Decreasing"
        else:
            trend = "➡ Stable"

        st.session_state.prev_volumes[symbol] = current_volume
        filtered_data.append((symbol, row["Price"], current_volume, trend, row["Timestamp"]))

    df_filtered = pd.DataFrame(filtered_data, columns=["Symbol", "Price", "Volume", "Trend", "Timestamp"])
    return df_filtered

# Convert UTC to IST
def convert_to_ist(utc_time):
    ist_time = utc_time + timedelta(hours=5, minutes=30)
    return ist_time.strftime("%I:%M:%S %p")

# Engulfing Candle Analysis (Dummy)
def check_engulfing_candle(symbol):
    """Simulated Engulfing Candle Detection."""
    recent_candles = [
        {"open": 100, "close": 105},  # 1H
        {"open": 105, "close": 110},  # 4H
        {"open": 98, "close": 115},   # 1D
        {"open": 90, "close": 120}    # 1W
    ]
    
    signals = []
    for timeframe, candle in zip(["1H", "4H", "1D", "1W"], recent_candles):
        if candle["close"] > candle["open"]:
            signals.append(f"{timeframe}: 🟢 Bullish")
        elif candle["close"] < candle["open"]:
            signals.append(f"{timeframe}: 🔴 Bearish")
        else:
            signals.append(f"{timeframe}: ⚪ Neutral")

    return ", ".join(signals)

# Fetch and process data
df = fetch_data()
if not df.empty:
    df_filtered = track_volume(df)
    df_filtered["Timestamp (IST)"] = df_filtered["Timestamp"].apply(convert_to_ist)
    df_filtered = df_filtered.drop(columns=["Timestamp"])
    df_filtered["Engulfing Signal"] = df_filtered["Symbol"].apply(check_engulfing_candle)

    # Display Data
    st.dataframe(df_filtered, height=600)

# Auto-refresh the app
st.experimental_rerun()
