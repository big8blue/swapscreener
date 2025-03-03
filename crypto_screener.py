import streamlit as st
import requests
import pandas as pd
import time
from datetime import datetime, timedelta

# OKX API URLs
TICKERS_URL = "https://www.okx.com/api/v5/market/tickers?instType=SWAP"
CANDLES_URL = "https://www.okx.com/api/v5/market/candles"

# Set Page Configuration
st.set_page_config(page_title="Crypto Screener", layout="wide")

st.title("🚀 Real-Time Crypto Futures Screener")

# Caching API Calls (refreshes every 5 seconds)
@st.cache_data(ttl=5)
def fetch_data():
    """Fetch all swap futures tickers from OKX API."""
    try:
        response = requests.get(TICKERS_URL, timeout=5)
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

        if symbol in st.session_state.prev_volumes:
            prev_volume = st.session_state.prev_volumes[symbol]
            if current_volume > prev_volume:
                trend = "🔼 Increasing"
                color = "green"
            elif current_volume < prev_volume:
                trend = "🔽 Decreasing"
                color = "red"
            else:
                trend = "➡ Stable"
                color = "gray"
        else:
            trend = "🆕 New"
            color = "blue"

        st.session_state.prev_volumes[symbol] = current_volume
        filtered_data.append((symbol, row["Price"], current_volume, trend, row["Timestamp"], color))

    df_filtered = pd.DataFrame(filtered_data, columns=["Symbol", "Price", "Volume", "Trend", "Timestamp", "Color"])
    return df_filtered

# Convert UTC to IST
def convert_to_ist(utc_time):
    ist_time = utc_time + timedelta(hours=5, minutes=30)
    return ist_time.strftime("%I:%M:%S %p")

# Fetch historical candles & detect engulfing pattern (only for displayed symbols)
@st.cache_data(ttl=60)
def check_engulfing_candle(symbols):
    """Fetch real candlestick data & detect engulfing patterns for multiple symbols."""
    timeframes = {"1H": "60m", "4H": "240m", "1D": "1D", "1W": "1W"}
    signals_dict = {}

    for symbol in symbols:
        signals = []
        for tf, okx_tf in timeframes.items():
            url = f"{CANDLES_URL}?instId={symbol}&bar={okx_tf}&limit=2"
            try:
                response = requests.get(url, timeout=3)
                data = response.json().get("data", [])
                if len(data) < 2:
                    signals.append(f"{tf}: ⚪ No Data")
                    continue

                prev_candle = data[1]  # Previous candle
                curr_candle = data[0]  # Current candle

                prev_open, prev_close = float(prev_candle[1]), float(prev_candle[4])
                curr_open, curr_close = float(curr_candle[1]), float(curr_candle[4])

                # Bullish Engulfing: Current green candle engulfs previous red candle
                if curr_open < prev_close and curr_close > prev_open:
                    signals.append(f"{tf}: 🟢 Bullish")
                # Bearish Engulfing: Current red candle engulfs previous green candle
                elif curr_open > prev_close and curr_close < prev_open:
                    signals.append(f"{tf}: 🔴 Bearish")
                else:
                    signals.append(f"{tf}: ⚪ Neutral")
            except:
                signals.append(f"{tf}: ⚪ Error")

        signals_dict[symbol] = ", ".join(signals)

    return signals_dict

# Live Data Display
placeholder = st.empty()

def update_display():
    """Updates the displayed data every 5 seconds."""
    df = fetch_data()
    if not df.empty:
        df_filtered = track_volume(df)
        df_filtered["Timestamp (IST)"] = df_filtered["Timestamp"].apply(convert_to_ist)
        df_filtered = df_filtered.drop(columns=["Timestamp"])

        # Fetch engulfing signals only for displayed symbols
        displayed_symbols = df_filtered["Symbol"].tolist()
        engulfing_signals = check_engulfing_candle(displayed_symbols)
        df_filtered["Engulfing Signal"] = df_filtered["Symbol"].map(engulfing_signals)

        with placeholder.container():
            st.dataframe(df_filtered, height=600)

# Auto-refresh every 5 seconds
st_autorefresh(interval=5000, key="data_refresh")

update_display()
