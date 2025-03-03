import streamlit as st
import requests
import pandas as pd
import pandas_ta as ta
import time
from datetime import datetime, timedelta
from streamlit_autorefresh import st_autorefresh

# OKX API endpoints
API_URL_TICKERS = "https://www.okx.com/api/v5/market/tickers?instType=SWAP"
API_URL_OI = "https://www.okx.com/api/v5/public/open-interest?instType=SWAP"

# Set Page Configuration
st.set_page_config(page_title="Crypto Futures Screener", layout="wide", initial_sidebar_state="expanded")

st.title("🚀 Advanced Crypto Futures Screener")

# Sidebar Controls
st.sidebar.header("🔍 Filters & Settings")
min_volume = st.sidebar.number_input("Min Volume (24h)", value=500000, step=100000)
refresh_rate = st.sidebar.slider("Refresh Rate (Seconds)", 1, 10, 1)
enable_alerts = st.sidebar.checkbox("Enable Telegram Alerts", value=False)

# Auto Refresh (Fixes While Loop Issue)
st_autorefresh(interval=refresh_rate * 1000, key="data_refresh")

@st.cache_data(ttl=1)
def fetch_data():
    """Fetches swap futures tickers and open interest from OKX API."""
    try:
        # Fetch tickers data
        response_tickers = requests.get(API_URL_TICKERS)
        data_tickers = response_tickers.json().get("data", [])
        if not data_tickers:
            return pd.DataFrame()

        df_tickers = pd.DataFrame(data_tickers)
        df_tickers = df_tickers[["instId", "last", "vol24h", "ts"]]
        df_tickers.columns = ["Symbol", "Price", "Volume", "Timestamp"]
        df_tickers["Price"] = df_tickers["Price"].astype(float)
        df_tickers["Volume"] = df_tickers["Volume"].astype(float)
        df_tickers["Timestamp"] = pd.to_datetime(df_tickers["Timestamp"], unit="ms")

        # Fetch Open Interest Data (if available)
        response_oi = requests.get(API_URL_OI)
        data_oi = response_oi.json().get("data", [])
        df_oi = pd.DataFrame(data_oi) if data_oi else pd.DataFrame()
        if not df_oi.empty:
            df_oi = df_oi[["instId", "oi"]]
            df_oi.columns = ["Symbol", "Open Interest"]
            df_oi["Open Interest"] = df_oi["Open Interest"].astype(float)

            # Merge with tickers
            df = pd.merge(df_tickers, df_oi, on="Symbol", how="left")
        else:
            df = df_tickers
            df["Open Interest"] = None  # Handle missing OI data

        return df
    except Exception as e:
        st.error(f"Error fetching data: {e}")
        return pd.DataFrame()

# Convert UTC to IST
def convert_to_ist(utc_time):
    ist_time = utc_time + timedelta(hours=5, minutes=30)
    return ist_time.strftime("%I:%M:%S %p")

# Calculate RSI and EMA
def calculate_indicators(df):
    df["EMA"] = df["Price"].ewm(span=20, adjust=False).mean()
    df["RSI"] = ta.rsi(df["Price"], length=14)
    return df

# Detect Volume Spikes
def detect_volume_spikes(df):
    df["Volume MA"] = df["Volume"].rolling(window=20).mean()
    df["Volume Spike"] = df["Volume"] > 1.5 * df["Volume MA"]
    return df

# Send Telegram Alert (Replacing Email)
def send_telegram_alert(symbol, indicator):
    TELEGRAM_BOT_TOKEN = "your_bot_token"
    TELEGRAM_CHAT_ID = "your_chat_id"
    message = f"🚨 Alert: {symbol} triggered {indicator} signal!"
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage?chat_id={TELEGRAM_CHAT_ID}&text={message}"
    requests.get(url)

# Fetch Data
df = fetch_data()

if not df.empty:
    df["Updated Time (IST)"] = df["Timestamp"].apply(convert_to_ist)
    df = df.drop(columns=["Timestamp"])
    df = df[df["Volume"] >= min_volume]  # Apply volume filter

    # Calculate indicators
    df = calculate_indicators(df)
    df = detect_volume_spikes(df)

    # Trigger Alerts
    if enable_alerts:
        for _, row in df.iterrows():
            if row["RSI"] > 70:
                send_telegram_alert(row["Symbol"], "RSI > 70")
            elif row["RSI"] < 30:
                send_telegram_alert(row["Symbol"], "RSI < 30")
            if row["Volume Spike"]:
                send_telegram_alert(row["Symbol"], "Volume Spike")

    # Display Data
    st.dataframe(df.sort_values(by="Volume", ascending=False), height=600)
else:
    st.warning("No data available. Please check API or network connection.")
