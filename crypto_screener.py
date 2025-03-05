import streamlit as st
import requests
import pandas as pd

# API Endpoints
API_URL = "https://api.coindcx.com/exchange/v1/derivatives/futures/data/active_instruments"
LTP_URL = "https://api.coindcx.com/exchange/v1/derivatives/futures/data/trades?pair="

st.set_page_config(page_title="Crypto Screener", layout="wide")
st.title("🚀 Real-Time Crypto Futures Screener")

st.sidebar.header("🔍 Filters")
refresh_rate = st.sidebar.slider("Refresh Rate (Seconds)", 1, 10, 1)

@st.cache_data(ttl=refresh_rate)
def fetch_futures_data():
    """Fetch all swap futures tickers from CoinDCX API."""
    try:
        response = requests.get(API_URL)
        data = response.json()  

        if isinstance(data, list):
            return pd.DataFrame(data)
        else:
            st.error("Unexpected API response format")
            return pd.DataFrame()

    except Exception as e:
        st.error(f"Error fetching futures data: {e}")
        return pd.DataFrame()

@st.cache_data(ttl=refresh_rate)
def fetch_ltp_data():
  import requests  # Install requests module first.
url = "https://api.coindcx.com/exchange/v1/derivatives/futures/data/trades?pair={instrument_name}"
#sample_url = "https://api.coindcx.com/exchange/v1/derivatives/futures/data/trades?pair=B-MKR_USDT"
response = requests.get(url)
data = response.json()
print(data)
# Fetch data
df_futures = fetch_futures_data()
df_ltp = fetch_ltp_data()

if not df_futures.empty and not df_ltp.empty:
    # Merge futures data with LTP
    df_merged = df_futures.merge(df_ltp, on="symbol", how="left")

    # Select relevant columns
    expected_columns = ["symbol", "mark_price", "volume", "timestamp", "LTP"]
    df_display = df_merged[[col for col in expected_columns if col in df_merged.columns]]

    # Convert timestamp if available
    if "timestamp" in df_display.columns:
        df_display["timestamp"] = pd.to_datetime(df_display["timestamp"], unit="ms")

    st.write("### 🔥 Crypto Futures with LTP")
    st.dataframe(df_display)

else:
    st.error("Failed to fetch data from APIs")
