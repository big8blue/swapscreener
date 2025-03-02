import streamlit as st
import requests
import pandas as pd
import time
from datetime import datetime, timedelta

# OKX API for all swap tickers
API_URL = "https://www.okx.com/api/v5/market/tickers?instType=SWAP"

st.set_page_config(page_title="Crypto Futures Screener", layout="wide")
st.title("🚀 Real-Time Crypto Futures Screener (All Futures Swaps)")

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
        # Convert the Timestamp to IST 12-hour format
        df["Timestamp"] = pd.to_datetime(df["Timestamp"], unit="ms")
        df["Timestamp (IST)"] = df["Timestamp"].apply(convert_to_ist)
        
        # Remove the original Timestamp column
        df = df.drop(columns=["Timestamp"])
        
        # Update the dataframe in the Streamlit app
        table_placeholder.dataframe(df, height=600)  # Updates the same box

    time.sleep(1)  # Refresh every second
