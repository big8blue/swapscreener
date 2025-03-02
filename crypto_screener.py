import streamlit as st
import requests
import pandas as pd
import time

# CoinDCX API for all tickers
API_URL = "https://public.coindcx.com/exchange/ticker"

st.set_page_config(page_title="Crypto Futures Screener", layout="wide")
st.title("🚀 Real-Time Crypto Futures Screener (USDT Pairs)")

# Initialize session state for historical prices and volume
if "prev_prices_5m" not in st.session_state:
    st.session_state.prev_prices_5m = {}
if "prev_prices_15m" not in st.session_state:
    st.session_state.prev_prices_15m = {}
if "timestamps_5m" not in st.session_state:
    st.session_state.timestamps_5m = {}
if "timestamps_15m" not in st.session_state:
    st.session_state.timestamps_15m = {}
if "prev_volumes" not in st.session_state:
    st.session_state.prev_volumes = {}

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
        df = df[["market", "last_price", "volume"]]
        df.columns = ["Symbol", "Price (USDT)", "Volume"]
        df["Price (USDT)"] = df["Price (USDT)"].astype(float)
        df["Volume"] = df["Volume"].astype(float)

        return df
    except Exception as e:
        st.error(f"Error fetching data: {e}")
        return pd.DataFrame()

def track_signals(df):
    """Track price momentum, RSI, EMA, and volume spikes."""
    current_time = pd.Timestamp.utcnow()
    price_5m, price_15m, signals, rsi_values, ema_values, volume_spikes = [], [], [], [], [], []

    for index, row in df.iterrows():
        symbol = row["Symbol"]
        current_price = row["Price (USDT)"]
        current_volume = row["Volume"]

        # Store & update 5-minute data
        if symbol not in st.session_state.prev_prices_5m:
            st.session_state.prev_prices_5m[symbol] = current_price
            st.session_state.timestamps_5m[symbol] = current_time
            price_5m.append("-")
        else:
            prev_time_5m = st.session_state.timestamps_5m[symbol]
            if (current_time - prev_time_5m).total_seconds() >= 300:  # 5 minutes
                price_5m.append(st.session_state.prev_prices_5m[symbol])
                st.session_state.prev_prices_5m[symbol] = current_price
                st.session_state.timestamps_5m[symbol] = current_time
            else:
                price_5m.append(st.session_state.prev_prices_5m[symbol])

        # Store & update 15-minute data
        if symbol not in st.session_state.prev_prices_15m:
            st.session_state.prev_prices_15m[symbol] = current_price
            st.session_state.timestamps_15m[symbol] = current_time
            price_15m.append("-")
        else:
            prev_time_15m = st.session_state.timestamps_15m[symbol]
            if (current_time - prev_time_15m).total_seconds() >= 900:  # 15 minutes
                price_15m.append(st.session_state.prev_prices_15m[symbol])
                st.session_state.prev_prices_15m[symbol] = current_price
                st.session_state.timestamps_15m[symbol] = current_time
            else:
                price_15m.append(st.session_state.prev_prices_15m[symbol])

        # Calculate RSI (Simple approximation)
        if isinstance(price_5m[-1], float):
            change = current_price - price_5m[-1]
            rsi = 100 - (100 / (1 + (max(change, 0) / abs(min(change, 0.0001)))))
            rsi_values.append(round(rsi, 2))
        else:
            rsi_values.append("-")

        # EMA Calculation (Simple Approximation)
        if index > 10:  # Require some history
            ema = (current_price * 0.1) + (df["Price (USDT)"].iloc[index - 1] * 0.9)
            ema_values.append(round(ema, 2))
        else:
            ema_values.append("-")

        # Volume Spike Detection
        if symbol not in st.session_state.prev_volumes:
            st.session_state.prev_volumes[symbol] = current_volume
            volume_spikes.append("-")
        else:
            prev_volume = st.session_state.prev_volumes[symbol]
            if current_volume > prev_volume * 1.5:
                volume_spikes.append("🔥 Spike")
            else:
                volume_spikes.append("-")
            st.session_state.prev_volumes[symbol] = current_volume

        # Generate Trading Signals
        if isinstance(price_5m[-1], float) and isinstance(price_15m[-1], float):
            change_5m = (current_price - price_5m[-1])
            change_15m = (current_price - price_15m[-1])

            if change_5m > 0 and change_15m > 0:
                if rsi_values[-1] != "-" and rsi_values[-1] < 30:
                    signals.append("🚀 Strong Buy (RSI Oversold)")
                else:
                    signals.append("🟢 Buy")
            elif change_5m < 0 and change_15m < 0:
                if rsi_values[-1] != "-" and rsi_values[-1] > 70:
                    signals.append("⚠️ Strong Sell (RSI Overbought)")
                else:
                    signals.append("🔴 Sell")
            elif volume_spikes[-1] == "🔥 Spike":
                signals.append("⚡ Volume Surge")
            elif ema_values[-1] != "-" and current_price > ema_values[-1]:
                signals.append("📈 EMA Bullish")
            elif ema_values[-1] != "-" and current_price < ema_values[-1]:
                signals.append("📉 EMA Bearish")
            else:
                signals.append("🔄 Neutral")
        else:
            signals.append("🔄 Neutral")

    df["Price 5m Ago"] = price_5m
    df["Price 15m Ago"] = price_15m
    df["RSI"] = rsi_values
    df["EMA"] = ema_values
    df["Volume Spike"] = volume_spikes
    df["Signal"] = signals

    return df

# Sorting options
sort_col = st.selectbox("Sort by:", ["Price (USDT)", "RSI", "EMA", "Volume"], index=0)
sort_order = st.radio("Order:", ["Descending", "Ascending"], index=0)

# Live updating table
table_placeholder = st.empty()

while True:
    df = fetch_data()
    if not df.empty:
        df = track_signals(df)

        # Convert "-" to NaN for sorting
        df.replace("-", "0", inplace=True)
        df[sort_col] = pd.to_numeric(df[sort_col], errors="coerce")
        df.sort_values(by=sort_col, ascending=(sort_order == "Ascending"), inplace=True)

        table_placeholder.dataframe(df, height=600)  # Updates the same box

    time.sleep(1)  # Refresh every second
