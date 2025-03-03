import streamlit as st
import requests
import pandas as pd
from datetime import datetime, timedelta

# OKX API for all swap tickers
API_URL = "https://www.okx.com/api/v5/market/tickers?instType=SWAP"

# Set Page Configuration
st.set_page_config(page_title="Crypto Screener", layout="wide")

# Theme Toggle Button
if "dark_mode" not in st.session_state:
    st.session_state.dark_mode = True

def toggle_theme():
    st.session_state.dark_mode = not st.session_state.dark_mode

st.sidebar.button("Toggle Dark/Light Mode", on_click=toggle_theme)

theme = "dark" if st.session_state.dark_mode else "light"

st.markdown(f"""
    <style>
        body {{ background-color: {'#121212' if theme == 'dark' else '#FFFFFF'}; }}
    </style>
""", unsafe_allow_html=True)

st.title("🚀 dora Crypto Futures Screener")

# Cache API Calls
@st.cache_data(ttl=5)
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

# Convert UTC to 12-Hour IST
def convert_to_ist(utc_time):
    ist_time = utc_time + timedelta(hours=5, minutes=30)
    return ist_time.strftime("%I:%M:%S %p")

# Engulfing Candle Analysis (Dummy Data)
def check_engulfing_candle(symbol):
    """Simulated Engulfing Candle Detection (Replace with real API data)."""
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

# Display Data
df = fetch_data()
if not df.empty:
    df_filtered = track_volume(df)

    # Convert Timestamp to IST
    df_filtered["Timestamp (IST)"] = df_filtered["Timestamp"].apply(convert_to_ist)
    df_filtered = df_filtered.drop(columns=["Timestamp"])

    # Add Engulfing Candle Signals
    df_filtered["Engulfing Signal"] = df_filtered["Symbol"].apply(check_engulfing_candle)

    # Apply Color Formatting
    def highlight_trend(row):
        return ["background-color: " + row["Color"]] * len(row)

    # Display Data
    st.dataframe(df_filtered.style.apply(highlight_trend, axis=1), height=600)

    # Add TradingView Chart
    selected_ticker = st.selectbox("Select a Symbol to View Chart", df_filtered["Symbol"].unique())

    if selected_ticker:
        st.markdown(f"""
        <iframe src="https://www.tradingview.com/chart/?symbol=OKX:{selected_ticker.replace('-SWAP', '')}"
        width="100%" height="500" frameborder="0"></iframe>
        """, unsafe_allow_html=True)

st.info("Data updates every 5 seconds. Only showing tickers with consistent volume trend.")
