import streamlit as st
import requests
import pandas as pd
import time

# CoinDCX API for futures market data (USDT pairs)
API_URL = "https://api.coindcx.com/exchange/v1/market_data/futures"

st.set_page_config(page_title="Crypto Futures Screener", layout="wide")
st.title("🚀 Real-Time Crypto Futures Screener (USDT Pairs)")

# Store historical prices for tracking changes
if "prev_prices_5m" not in st.session_state:
    st.session_state.prev_prices_5m = {}

if "prev_prices_15m" not in st.session_state:
    st.session_state.prev_prices_15m = {}

if "timestamps_5m" not in st.session_state:
    st.session_state.timestamps_5m = {}

if "timestamps_15m" not in st.session_state:
    st.session_state.timestamps_15m = {}

@st.cache_data(ttl=5)  # Cache data for 5 seconds to reduce API calls
def fetch_data():
    """Fetch all USDT futures tickers from CoinDCX API."""
    try:
        response = requests.get(API_URL)
        data = response.json()
        if not data.get("data"):
            return pd.DataFrame()

        # Extract market data
        df = pd.DataFrame(data["data"])
        
        # Filter only USDT pairs (CoinDCX typically uses symbols like BTC_USDT)
        df = df[df["symbol"].str.endswith("USDT")]

        # Extract necessary columns and rename them
        df = df[["symbol", "last_price", "open_time"]]
        df.columns = ["Symbol", "Price (USDT)", "Timestamp"]

        # Convert the price to float and timestamp to readable format
        df["Price (USDT)"] = df["Price (USDT)"].astype(float)
        df["Timestamp"] = pd.to_datetime(df["Timestamp"], unit="ms")

        return df
    except Exception as e:
        st.error(f"Error fetching data: {e}")
        return pd.DataFrame()

def track_price_history(df):
    """Track 5-minute and 15-minute prices and generate signals."""
    current_time = pd.Timestamp.utcnow()
    price_5m, price_15m, signals = [], [], []

    for index, row in df.iterrows():
        symbol = row["Symbol"]
        current_price = row["Price (USDT)"]

        # Store & update 5-minute data
        if symbol not in st.session_state.prev_prices_5m:
            st.session_state.prev_prices_5m[symbol] = current_price
            st.session_state.timestamps_5m[symbol] = current_time
            price_5m.append("-")
        else:
            prev_time_5m = st.session_state.timestamps_5m[symbol]
            time_diff_5m = (current_time - prev_time_5m).total_seconds() / 60  # Convert to minutes

            if time_diff_5m >= 5:
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
            time_diff_15m = (current_time - prev_time_15m).total_seconds() / 60  # Convert to minutes

            if time_diff_15m >= 15:
                price_15m.append(st.session_state.prev_prices_15m[symbol])
                st.session_state.prev_prices_15m[symbol] = current_price
                st.session_state.timestamps_15m[symbol] = current_time
            else:
                price_15m.append(st.session_state.prev_prices_15m[symbol])

        # Generate Buy/Sell signals
        if isinstance(price_5m[-1], float) and isinstance(price_15m[-1], float):
            change_5m = (current_price - price_5m[-1])
            change_15m = (current_price - price_15m[-1])

            if change_5m > 0 and change_15m > 0:
                signals.append("🚀 Buy")
            elif change_5m < 0 and change_15m < 0:
                signals.append("⚠️ Sell")
            else:
                signals.append("🔄 Neutral")
        else:
            signals.append("🔄 Neutral")

    df["Price 5m Ago"] = price_5m
    df["Price 15m Ago"] = price_15m
    df["Signal"] = signals

    return df

# Sort options
sort_col = st.selectbox("Sort by:", ["Price (USDT)", "Price 5m Ago", "Price 15m Ago"], index=0)
sort_order = st.radio("Order:", ["Descending", "Ascending"], index=0)

# Create a single placeholder for dynamic updates
table_placeholder = st.empty()

while True:
    df = fetch_data()
    if not df.empty:
        df = track_price_history(df)

        # Sort data based on selection
        df.replace("-", "0", inplace=True)  # Convert "-" to "0" for sorting
        df[sort_col] = pd.to_numeric(df[sort_col], errors="coerce")
        df.sort_values(by=sort_col, ascending=(sort_order == "Ascending"), inplace=True)
        
        table_placeholder.dataframe(df, height=600)  # Updates the same box

    time.sleep(1)  # Refresh every second
