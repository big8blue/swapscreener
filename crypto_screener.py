import streamlit as st
import requests
import pandas as pd
import time
from datetime import datetime, timedelta

# OKX API for all swap tickers
API_URL = "https://www.okx.com/api/v5/market/tickers?instType=SWAP"

st.set_page_config(page_title="Crypto Futures Screener", layout="wide")
st.title("🚀 Real-Time Crypto Futures Screener (All Futures Swaps)")

# Store historical prices for tracking changes
if "prev_prices" not in st.session_state:
    st.session_state.prev_prices = {}
    st.session_state.prev_update_times = {}

@st.cache_data(ttl=5)  # Cache data for 5 seconds to reduce API calls
def fetch_data():
    """Fetch all swap futures tickers from OKX API."""
    try:
        response = requests.get(API_URL)
        data = response.json().get("data", [])
        if not data:
            return pd.DataFrame()

        # Convert the data into a DataFrame
        df = pd.DataFrame(data)

        # Filter to get swap instruments only (already filtered by the API)
        df = df[["instId", "last", "ts"]]
        df.columns = ["Symbol", "Price (USDT)", "Timestamp"]
        df["Price (USDT)"] = df["Price (USDT)"].astype(float)
        df["Timestamp"] = pd.to_datetime(df["Timestamp"], unit="ms")

        return df
    except Exception as e:
        st.error(f"Error fetching data: {e}")
        return pd.DataFrame()

def convert_to_ist(utc_time):
    """Convert UTC time to IST and format in 12-hour format with AM/PM."""
    ist_time = utc_time + timedelta(hours=5, minutes=30)  # Convert UTC to IST
    return ist_time.strftime("%I:%M:%S %p")  # Format in 12-hour with AM/PM

# Create a single placeholder for dynamic updates
table_placeholder = st.empty()

while True:
    df = fetch_data()
    if not df.empty:
        # Current time in IST (when data was fetched)
        current_ist_time = convert_to_ist(pd.Timestamp.utcnow())

        # Initialize or update last updated times for each symbol
        last_updated_times = []
        for index, row in df.iterrows():
            symbol = row["Symbol"]
            if symbol not in st.session_state.prev_update_times:
                # If this is the first time, set the current time as the last updated time
                st.session_state.prev_update_times[symbol] = current_ist_time
            last_updated_times.append(st.session_state.prev_update_times[symbol])

        # Add both current time and last updated time to the dataframe
        df["Current Time (IST)"] = current_ist_time
        df["Last Updated Time (IST)"] = last_updated_times
        
        # Update the dataframe in the Streamlit app
        table_placeholder.dataframe(df, height=600)  # Updates the same box

    time.sleep(1)  # Refresh every second
