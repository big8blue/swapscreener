import streamlit as st
import requests
import pandas as pd
import time

# CoinDCX API URLs
ACTIVE_FUTURES_URL = "https://api.coindcx.com/exchange/v1/derivatives/futures/data/active_instruments"
MARKET_DATA_URL = "https://api.coindcx.com/market_data"

# Function to fetch active futures instruments
def get_active_instruments(margin_currency="USDT"):
    url = f"{ACTIVE_FUTURES_URL}?margin_currency_short_name[]={margin_currency}"
    response = requests.get(url)
    
    if response.status_code == 200:
        return response.json()
    else:
        st.error("⚠️ Error fetching active futures!")
        return []

# Function to fetch live market data
def get_market_data():
    response = requests.get(MARKET_DATA_URL)
    if response.status_code == 200:
        return response.json()
    else:
        st.error("⚠️ Error fetching market data!")
        return {}

# Streamlit UI
st.set_page_config(page_title="CoinDCX Futures Screener", layout="wide")
st.title("📊 CoinDCX Futures Screener (Real-Time)")

# Select margin mode (USDT or INR)
margin_currency = st.selectbox("Select Margin Currency:", ["USDT", "INR"])

# Fetch instrument list
instruments = get_active_instruments(margin_currency)

# Fetch live market data
market_data = get_market_data()

# Process and display data
if instruments and market_data:
    futures_data = []
    for instrument in instruments:
        symbol = instrument.get("symbol")
        if symbol in market_data:
            market_info = market_data[symbol]
            futures_data.append({
                "Symbol": symbol,
                "Last Price": market_info.get("last_price"),
                "24h High": market_info.get("high"),
                "24h Low": market_info.get("low"),
                "24h Volume": market_info.get("volume"),
            })

    # Convert to DataFrame and display
    df = pd.DataFrame(futures_data)
    st.dataframe(df, use_container_width=True)
else:
    st.write("No data available.")

# Auto-refresh every 5 seconds
time.sleep(5)
st.rerun()
