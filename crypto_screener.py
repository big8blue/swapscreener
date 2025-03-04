import streamlit as st
import requests
import pandas as pd
import time

# API Endpoint for CoinDCX Futures Market
COINDCX_FUTURES_API = "https://api.coindcx.com/exchange/v1/markets"

# Function to fetch live futures market data
def fetch_futures_data():
    response = requests.get(COINDCX_FUTURES_API)
    if response.status_code == 200:
        return response.json()
    return []

# Streamlit UI
st.title("📊 Real-Time Crypto Futures Screener (CoinDCX)")

# User selects refresh rate
refresh_rate = st.sidebar.slider("Refresh Rate (seconds)", 1, 10, 3)

# Data Processing
while True:
    futures_data = fetch_futures_data()
    if not futures_data:
        st.error("⚠️ Failed to fetch market data!")
        time.sleep(refresh_rate)
        continue

    # Convert data to DataFrame
    df = pd.DataFrame(futures_data)

    # Filter only FUTURES contracts
    df = df[df['market_type'] == 'futures'][['symbol', 'base_currency_short_name', 'quote_currency_short_name', 'target_currency_short_name', 'min_quantity', 'max_quantity']]

    # Display Table
    st.dataframe(df)

    # Refresh data at the selected interval
    time.sleep(refresh_rate)
    st.rerun()
