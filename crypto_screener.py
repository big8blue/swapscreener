import streamlit as st
import requests
import pandas as pd

# CoinDCX API for all tickers
API_URL = "https://public.coindcx.com/exchange/ticker"

st.set_page_config(page_title="Crypto Futures Screener", layout="wide")
st.title("🚀 Real-Time Crypto Futures Screener (USDT Pairs)")

# Initialize session state for historical prices
if "prev_prices_5m" not in st.session_state:
    st.session_state.prev_prices_5m = {}
if "prev_prices_15m" not in st.session_state:
    st.session_state.prev_prices_15m = {}
if "timestamps_5m" not in st.session_state:
    st.session_state.timestamps_5m = {}
if "timestamps_15m" not in st.session_state:
    st.session_state.timestamps_15m = {}

@st.cache_data(ttl=5)  # Cache data for 5 seconds
def fetch_data():
    """Fetch all USDT pair tickers from CoinDCX API."""
    try:
        response = requests.get(API_URL)
        data = response.json()
        if not data:
            st.warning("No data returned from the API.")
            return pd.DataFrame()

        # Convert to DataFrame
        df = pd.DataFrame(data)

        # Filter for USDT pairs
        df = df[df["market"].str.endswith("USDT")]

        # Select relevant columns
        df = df[["market", "last_price", "timestamp"]]
        df.columns = ["Symbol", "Price (USDT)", "Timestamp"]
        df["Price (USDT)"] = df["Price (USDT)"].astype(float)
        df["Timestamp"] = pd.to_datetime(df["Timestamp"], unit="s")

        return df
    except Exception as e:
        st.error(f"Error fetching data: {e}")
        return pd.DataFrame()

def track_price_history(df):
    """Track 5-minute and 15-minute prices and generate signals."""
    current_time = pd.Timestamp.utcnow()
    signals = []

    for _, row in df.iterrows():
        symbol = row["Symbol"]
        current_price = row["Price (USDT)"]

        # 5-minute tracking
        if symbol not in st.session_state.prev_prices_5m:
            st.session_state.prev_prices_5m[symbol] = current_price
            st.session_state.timestamps_5m[symbol] = current_time
            signals.append("🔄 Neutral")
        else:
            prev_time_5m = st.session_state.timestamps_5m[symbol]
            time_diff_5m = (current_time - prev_time_5m).total_seconds() / 60

            if time_diff_5m >= 5:
                # Generate signals based on price movement
                prev_price_5m = st.session_state.prev_prices_5m[symbol]
                change_5m = current_price - prev_price_5m

                if change_5m > 0:
                    signals.append("🚀 Buy")
                elif change_5m < 0:
                    signals.append("⚠️ Sell")
                else:
                    signals.append("🔄 Neutral")

                # Update the previous price and timestamp
                st.session_state.prev_prices_5m[symbol] = current_price
                st.session_state.timestamps_5m[symbol] = current_time
            else:
                signals.append("🔄 Neutral")

    df["Signal"] = signals
    return df

# Sorting options
sort_col = st.selectbox("Sort by:", ["Price (USDT)"], index=0)
sort_order = st.radio("Order:", ["Descending", "Ascending"], index=0)

# Placeholder for dynamic updates
table_placeholder = st.empty()

# Fetching and displaying the data with auto-refresh
df = fetch_data()
if not df.empty:
    df = track_price_history(df)

    # Sort data
    df[sort_col] = pd.to_numeric(df[sort_col], errors="coerce")
    df.sort_values(by=sort_col, ascending=(sort_order == "Ascending"), inplace=True)

    table_placeholder.dataframe(df, height=600)

# Use Streamlit's rerun mechanism for auto-refresh
st.experimental_rerun()  # Automatically refresh the app every second
