import streamlit as st
import pandas as pd
import requests
import time

# CoinDCX API Endpoint
API_URL = "https://api.coindcx.com/exchange/v1/derivatives/futures/data/active_instruments?margin_currency_short_name[]=USDT"

# Sidebar input for refresh rate
refresh_rate = st.sidebar.slider("Refresh Interval (seconds)", 1, 60, 5)

def fetch_futures_data():
    """Fetches real-time futures data from CoinDCX."""
    try:
        response = requests.get(API_URL)
        if response.status_code == 200:
            data = response.json()
            df = pd.DataFrame([
                {
                    "Pair": item.get("contract_name", "N/A"),
                    "LTP": item.get("last_price", "N/A"),
                    "Updated Time": time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
                }
                for item in data
            ])
            return df
        else:
            st.error("Error fetching data from CoinDCX API!")
            return pd.DataFrame()
    except Exception as e:
        st.error(f"Exception: {e}")
        return pd.DataFrame()

st.title("CoinDCX Crypto Futures Screener")
st.write("Displaying real-time futures data from CoinDCX.")

while True:
    df = fetch_futures_data()
    if not df.empty:
        st.dataframe(df)
    time.sleep(refresh_rate)
    st.experimental_rerun()
