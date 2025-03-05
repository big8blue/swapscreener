import streamlit as st
import requests
import pandas as pd

# API URLs
API_URL = "https://api.coindcx.com/exchange/v1/derivatives/futures/data/active_instruments"
LTP_API_URL = "https://public.coindcx.com/market_data/v3/current_prices/futures/rt"

# Streamlit Page Configuration
st.set_page_config(page_title="Crypto Screener", layout="wide")
st.title("🚀 Real-Time Crypto Futures Screener")

st.sidebar.header("🔍 Filters")

# Set refresh rate
refresh_rate = st.sidebar.slider("Refresh Rate (Seconds)", 1, 10, 1)

@st.cache_data(ttl=refresh_rate)
def fetch_data():
    """Fetch all swap futures tickers from CoinDCX API."""
    try:
        response = requests.get(API_URL)
        data = response.json()
        return pd.DataFrame(data) if isinstance(data, list) else None
    except Exception as e:
        st.error(f"Error fetching data: {e}")
        return None

@st.cache_data(ttl=refresh_rate)
def fetch_ltp():
    """Fetch real-time Last Traded Price (LTP) for all futures symbols."""
    try:
        response = requests.get(LTP_API_URL)
        data = response.json()
        return pd.DataFrame(data["prices"]) if "prices" in data else None
    except Exception as e:
        st.error(f"Error fetching LTP data: {e}")
        return None

# Fetch data
df = fetch_data()
ltp_df = fetch_ltp()

if df is not None and ltp_df is not None:
    # Rename columns for clarity
    ltp_df.rename(columns={"i": "symbol", "b": "ltp"}, inplace=True)

    # Merge instrument data with LTP
    df = df.merge(ltp_df, on="symbol", how="left")

    # Select relevant columns
    selected_columns = ["symbol", "ltp", "mark_price", "volume", "timestamp"]
    available_columns = [col for col in selected_columns if col in df.columns]
    df_filtered = df[available_columns]

    # Convert timestamp if available
    if "timestamp" in df_filtered.columns:
        df_filtered["timestamp"] = pd.to_datetime(df_filtered["timestamp"], unit='ms')

    # Display processed data
    st.write("### Processed Data with LTP")
    st.dataframe(df_filtered)

else:
    st.error("Failed to fetch data from API.")
