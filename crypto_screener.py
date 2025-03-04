import streamlit as st
import requests
import pandas as pd
import time

# API URL for active futures instruments
BASE_URL = "https://api.coindcx.com/exchange/v1/derivatives/futures/data/active_instruments"

# Function to fetch active instruments
def get_active_instruments(margin_currency="USDT"):
    url = f"{BASE_URL}?margin_currency_short_name[]={margin_currency}"
    response = requests.get(url)
    
    if response.status_code == 200:
        return response.json()
    else:
        st.error("⚠️ Error fetching data!")
        return []

# Streamlit UI
st.title("📊 CoinDCX Active Futures Instruments")

# Select margin mode (USDT or INR)
margin_currency = st.selectbox("Select Margin Currency:", ["USDT", "INR"])

# Fetch instrument list
instruments = get_active_instruments(margin_currency)

# Convert to DataFrame
if instruments:
    df = pd.DataFrame(instruments, columns=["symbol"])
    st.dataframe(df)
else:
    st.write("No data available.")

# Auto-refresh every 5 seconds
time.sleep(5)
st.rerun()
