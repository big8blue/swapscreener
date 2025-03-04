import streamlit as st
import pandas as pd
import requests
import time

st.set_page_config(page_title="CoinDCX Futures Screener", layout="wide")

API_URL = "https://api.coindcx.com/exchange/v1/derivatives/futures/data/active_instruments?margin_currency_short_name[]=USDT"

# Sidebar Refresh Control
refresh_rate = st.sidebar.slider("Refresh every (seconds)", 1, 10, 5)

@st.cache_data(ttl=10)  # Cache for 10 seconds to reduce API calls
def fetch_futures_data():
    response = requests.get(API_URL)
    if response.status_code == 200:
        return response.json()
    else:
        return []

# Main UI
st.title("📊 CoinDCX Futures Screener")
st.markdown("### Live Futures Market Data")

while True:
    futures_data = fetch_futures_data()
    
    if futures_data:
        df = pd.DataFrame(futures_data)
        df = df.rename(columns={"contract_name": "Pair", "last_price": "LTP"})
        
        # Add timestamp
        df["Updated Time"] = pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Display DataFrame
        st.dataframe(df[["Pair", "LTP", "Updated Time"]])
    
    # Refresh logic
    time.sleep(refresh_rate)
    st.experimental_rerun()  # Restart the script safely
