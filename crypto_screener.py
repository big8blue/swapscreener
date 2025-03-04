import streamlit as st
import requests
import pandas as pd
import time
from datetime import datetime, timedelta

API_URL = "https://api.coindcx.com/exchange/v1/derivatives/futures/data/active_instruments"

st.set_page_config(page_title="Crypto Screener", layout="wide")
st.title("🚀 Real-Time Crypto Futures Screener")

st.sidebar.header("🔍 Filters")

st.sidebar.subheader("📊 Volume Range (in Millions)")
col1, col2 = st.sidebar.columns(2)
min_volume_input = col1.number_input("Min Volume (M)", min_value=0.0, max_value=1000.0, value=0.5, step=0.1)
max_volume_input = col2.number_input("Max Volume (M)", min_value=0.0, max_value=1000.0, value=50.0, step=0.1)

min_volume, max_volume = st.sidebar.slider("Or use the slider below",
                                           min_value=0.0, max_value=1000.0,
                                           value=(min_volume_input, max_volume_input), step=0.1)

refresh_rate = st.sidebar.slider("Refresh Rate (Seconds)", 1, 10, 1)

@st.cache_data(ttl=refresh_rate)
def fetch_data():
    """Fetch all swap futures tickers from CoinDCX API."""
    try:
        response = requests.get(API_URL)
        data = response.json()  # Convert response to JSON

        st.write("### Raw API Response:")
        st.json(data)  # This will show the full response in Streamlit

        return data  # Return data as it is to analyze

    except Exception as e:
        st.error(f"Error fetching data: {e}")
        return None

data = fetch_data()
