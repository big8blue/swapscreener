import streamlit as st
import requests
import pandas as pd

API_URL = "https://www.okx.com/api/v5/market/tickers?instType=SWAP"

st.set_page_config(page_title="Crypto Futures Screener", layout="wide")
st.title("🚀 Real-Time Crypto Futures Screener")

@st.cache_data(ttl=10)  # Cache data for 10 seconds to reduce API calls
def fetch_data():
    try:
        response = requests.get(API_URL)
        data = response.json().get("data", [])
        df = pd.DataFrame(data)[["instId", "last"]]
        df.columns = ["Symbol", "Price (USDT)"]
        return df
    except Exception as e:
        st.error(f"Error fetching data: {e}")
        return pd.DataFrame()

# Auto-refresh every second
st_autorefresh = st.empty()

while True:
    df = fetch_data()
    st_autorefresh.dataframe(df, height=600)
    st.experimental_rerun()  # Refresh the script


