import streamlit as st
import requests
import pandas as pd

# API URLs
INSTRUMENTS_API = "https://api.coindcx.com/exchange/v1/derivatives/futures/data/active_instruments"
LTP_API = "https://public.coindcx.com/market_data/v3/current_prices/futures/rt"

# Streamlit UI Setup
st.set_page_config(page_title="Crypto Screener", layout="wide")
st.title("🚀 Real-Time Crypto Futures Screener")

st.sidebar.header("🔍 Filters")
refresh_rate = st.sidebar.slider("Refresh Rate (Seconds)", 1, 10, 1)

@st.cache_data(ttl=refresh_rate)
def fetch_data():
    """Fetch all swap futures tickers from CoinDCX API."""
    try:
        response = requests.get(INSTRUMENTS_API)
        data = response.json()
        return data if isinstance(data, list) else None
    except Exception as e:
        st.error(f"Error fetching futures data: {e}")
        return None

@st.cache_data(ttl=refresh_rate)
def fetch_ltp():
    """Fetch real-time Last Traded Prices (LTP) from CoinDCX API."""
    try:
        response = requests.get(LTP_API)
        data = response.json()
        return {item["s"]: item["p"] for item in data.get("data", [])}  # Convert to dictionary {symbol: price}
    except Exception as e:
        st.error(f"Error fetching LTP: {e}")
        return {}

# Fetch Data
data = fetch_data()
ltp_data = fetch_ltp()

if data:
    df = pd.DataFrame(data)

    # Extract relevant columns
    expected_columns = ["symbol", "mark_price", "volume", "timestamp"]
    available_columns = [col for col in expected_columns if col in df.columns]

    if available_columns:
        df_filtered = df[available_columns]

        # Convert timestamp
        if "timestamp" in df_filtered.columns:
            df_filtered["timestamp"] = pd.to_datetime(df_filtered["timestamp"], unit='ms')

        # Add LTP Column
        df_filtered["LTP"] = df_filtered["symbol"].map(ltp_data)

        # Display data
        st.write("### Processed Data with LTP")
        st.dataframe(df_filtered)
    else:
        st.error("Expected columns are missing from API response")
