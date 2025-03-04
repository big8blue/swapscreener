import streamlit as st
import requests
import pandas as pd

API_URL = "https://api.coindcx.com/exchange/v1/derivatives/futures/data/active_instruments"
LTP_API_URL = "https://api.coindcx.com/market_data/current_prices"

st.set_page_config(page_title="Crypto Screener", layout="wide")
st.title("🚀 Real-Time Crypto Futures Screener")

st.sidebar.header("🔍 Filters")
refresh_rate = st.sidebar.slider("Refresh Rate (Seconds)", 1, 10, 1)

@st.cache_data(ttl=refresh_rate)
def fetch_data():
    """Fetch all active futures symbols from CoinDCX API."""
    try:
        response = requests.get(API_URL, timeout=10)
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"API Error: {response.status_code}")
            return None
    except requests.exceptions.RequestException as e:
        st.error(f"❌ Network Error: {e}")
        return None

@st.cache_data(ttl=refresh_rate)
def fetch_ltp(symbols):
    """Fetch Last Traded Price (LTP) for given symbols."""
    try:
        payload = {"market": symbols}  # CoinDCX API expects a list of markets
        response = requests.post(LTP_API_URL, json=payload, timeout=10)
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"LTP API Error: {response.status_code}")
            return None
    except requests.exceptions.RequestException as e:
        st.error(f"❌ Network Error: {e}")
        return None

# Fetch Futures Data
data = fetch_data()

if data:
    # Extract Symbols
    df = pd.DataFrame(data)
    df = df[['symbol']]  # Keep only the symbol column
    
    # Fetch LTP for each symbol
    symbols = df['symbol'].tolist()
    ltp_data = fetch_ltp(symbols)

    if ltp_data:
        # Convert LTP response to a dictionary for easy lookup
        ltp_dict = {item['market']: item['price'] for item in ltp_data}

        # Add LTP column to DataFrame
        df['LTP'] = df['symbol'].map(ltp_dict)
    
    st.write("### Crypto Futures Data with LTP")
    st.dataframe(df)
else:
    st.warning("⚠️ No data received from API.")
