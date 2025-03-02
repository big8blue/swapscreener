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
if "timestamps_5m" not in st.session_state:
    st.session_state.timestamps_5m = {}

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

# Sorting options
sort_col = st.selectbox("Sort by:", ["Price (USDT)"], index=0)
sort_order = st.radio("Order:", ["Descending", "Ascending"], index=0)

# Placeholder for dynamic updates
table_placeholder = st.empty()

# Fetching and displaying the data with auto-refresh
df = fetch_data()
if not df.empty:
    # Sort data
    df[sort_col] = pd.to_numeric(df[sort_col], errors="coerce")
    df.sort_values(by=sort_col, ascending=(sort_order == "Ascending"), inplace=True)

    table_placeholder.dataframe(df[["Symbol", "Price (USDT)", "Timestamp"]], height=600)

# Use Streamlit's rerun mechanism for auto-refresh every few seconds
st.experimental_rerun()  # This will automatically refresh every few seconds
