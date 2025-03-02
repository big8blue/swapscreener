import streamlit as st
import requests
import pandas as pd
import time

# OKX API URL for all swap tickers
API_URL = "https://www.okx.com/api/v5/market/tickers?instType=SWAP"

st.set_page_config(page_title="Crypto Futures Screener", layout="wide")
st.title("🚀 Real-Time Crypto Futures Screener (All Swaps)")

# Store historical prices for tracking 5-minute changes
if "prev_prices" not in st.session_state:
    st.session_state.prev_prices = {}

if "timestamps" not in st.session_state:
    st.session_state.timestamps = {}

@st.cache_data(ttl=5)  # Cache data for 5 seconds to reduce API calls
def fetch_data():
    """Fetch all swap tickers from OKX API."""
    try:
        response = requests.get(API_URL)
        data = response.json().get("data", [])
        if not data:
            return pd.DataFrame()

        df = pd.DataFrame(data)
        df = df[["instId", "last", "ts"]]
        df.columns = ["Symbol", "Price (USDT)", "Timestamp"]
        df["Price (USDT)"] = df["Price (USDT)"].astype(float)
        df["Timestamp"] = pd.to_datetime(df["Timestamp"], unit="ms")
        
        return df
    except Exception as e:
        st.error(f"Error fetching data: {e}")
        return pd.DataFrame()

def calculate_5m_change(df):
    """Calculate 5-minute price change (%) for all swaps."""
    current_time = pd.Timestamp.utcnow()
    
    changes = []
    for index, row in df.iterrows():
        symbol = row["Symbol"]
        current_price = row["Price (USDT)"]
        
        # Store historical price if not available
        if symbol not in st.session_state.prev_prices:
            st.session_state.prev_prices[symbol] = current_price
            st.session_state.timestamps[symbol] = current_time
            changes.append("-")
            continue

        # Check if 5 minutes have passed
        prev_time = st.session_state.timestamps[symbol]
        prev_price = st.session_state.prev_prices[symbol]
        time_diff = (current_time - prev_time).total_seconds() / 60  # Convert to minutes

        if time_diff >= 5:
            price_change = ((current_price - prev_price) / prev_price) * 100
            changes.append(f"{price_change:.2f}%")
            st.session_state.prev_prices[symbol] = current_price  # Update price
            st.session_state.timestamps[symbol] = current_time  # Update timestamp
        else:
            changes.append("-")

    df["5m Change (%)"] = changes
    return df

# Create a single placeholder for dynamic updates
table_placeholder = st.empty()

while True:
    df = fetch_data()
    if not df.empty:
        df = calculate_5m_change(df)
        table_placeholder.dataframe(df, height=600)  # Updates the same box

    time.sleep(1)  # Refresh every second
