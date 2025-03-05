import streamlit as st
import requests
import pandas as pd

# API URLs
INSTRUMENTS_API = "https://api.coindcx.com/exchange/v1/derivatives/futures/data/active_instruments"
TRADE_HISTORY_API = "https://api.coindcx.com/exchange/v1/derivatives/futures/data/trades?pair={}"

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

        # Print response structure for debugging
        st.write("### Debug: API Response Sample")
        st.json(data[:3])  # Show first 3 entries

        return data if isinstance(data, list) else None
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
        return None  # Return None if error occurs

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

        # Fetch LTP for each symbol (Loop with progress bar)
        ltp_values = []
        progress_bar = st.progress(0)

        for idx, symbol in enumerate(df_filtered["symbol"]):
            ltp = fetch_ltp(symbol)
            ltp_values.append(ltp if ltp is not None else "N/A")
            progress_bar.progress((idx + 1) / len(df_filtered))

        df_filtered["LTP"] = ltp_values  # Add LTP Column

        # Display processed data
        st.write("### Processed Data with LTP")
        st.dataframe(df_filtered)
    else:
        st.error("No matching columns found. Check the API response above.")
