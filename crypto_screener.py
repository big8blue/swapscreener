import streamlit as st
import requests
import pandas as pd

# API URL
ACTIVE_FUTURES_URL = "https://api.coindcx.com/exchange/v1/derivatives/futures/data/active_instruments?margin_currency_short_name[]=USDT"

# Fetch data
response = requests.get(ACTIVE_FUTURES_URL)
if response.status_code == 200:
    futures_data = response.json()
else:
    st.error("⚠️ API Fetch Error!")
    futures_data = []

# Convert to DataFrame
if futures_data:
    df = pd.DataFrame(futures_data)
    st.title("📊 CoinDCX Futures Screener")
    st.dataframe(df)
else:
    st.write("No data available.")
