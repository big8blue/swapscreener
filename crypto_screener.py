import streamlit as st
import requests
import pandas as pd

# Correct API URL
INSTRUMENTS_API = "https://api.coindcx.com/exchange/v1/derivatives/futures/data/active_instruments"
TRADE_HISTORY_API = "https://api.coindcx.com/exchange/v1/derivatives/futures/data/trades?pair={}"

st.set_page_config(page_title="Crypto Screener", layout="wide")
st.title("🚀 Real-Time Crypto Futures Screener")

st.sidebar.header("🔍 Filters")
refresh_rate = st.sidebar.slider("Refresh Rate (Seconds)", 1, 10, 1)

@st.cache_data(ttl=refresh_rate)
def fetch_data():
    """Fetch futures instrument data from CoinDCX API."""
    try:
        response = requests.get(INSTRUMENTS_API)
        data = response.json()

        if isinstance(data, list) and all(isinstance(i, dict) for i in data):
            return data  # If response is a list of dictionaries
        elif isinstance(data, list):
            st.error("API returned only symbols, not full instrument data.")
            return None
        else:
            st.error("Unexpected API response format.")
            return None
    except Exception as e:
        st.error(f"Error fetching futures data: {e}")
        return None

def fetch_ltp(symbol):
    """Fetch the latest traded price (LTP) for a specific symbol."""
    try:
        response = requests.get(TRADE_HISTORY_API.format(symbol))
        trade_data = response.json()

        if isinstance(trade_data, list) and trade_data:
            return float(trade_data[0]["p"])  # Extract latest trade price
        return None
    except Exception as e:
        return None

# Fetch Data
data = fetch_data()

if data:
    df = pd.DataFrame(data)

    # Show available columns
    st.write("### Debug: Available Columns in API Response")
    st.write(df.columns.tolist())

    # Extract available columns dynamically
    essential_columns = ["symbol", "mark_price", "volume", "timestamp"]
    available_columns = [col for col in essential_columns if col in df.columns]

    if available_columns:
        df_filtered = df[available_columns]

        # Convert timestamp if available
        if "timestamp" in df_filtered.columns:
            df_filtered["timestamp"] = pd.to_datetime(df_filtered["timestamp"], unit='ms')

        # Fetch LTP for each symbol
        df_filtered["LTP"] = df_filtered["symbol"].apply(fetch_ltp)

        # Display processed data
        st.write("### Processed Data with LTP")
        st.dataframe(df_filtered)
    else:
        st.error("No matching columns found. The API may not be returning full instrument data.")
