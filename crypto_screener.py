import streamlit as st
import requests
import pandas as pd

API_URL = "https://api.coindcx.com/exchange/v1/derivatives/futures/data/active_instruments"

st.set_page_config(page_title="Crypto Screener", layout="wide")
st.title("🚀 Real-Time Crypto Futures Screener")

st.sidebar.header("🔍 Filters")
refresh_rate = st.sidebar.slider("Refresh Rate (Seconds)", 1, 10, 1)

@st.cache_data(ttl=refresh_rate)
def fetch_data():
    """Fetch all swap futures tickers from CoinDCX API."""
    try:
        st.write("Fetching data...")  # Debugging Log
        response = requests.get(API_URL, timeout=10)  # Add timeout
        if response.status_code == 200:
            data = response.json()
            st.write("✅ API Response Received")  # Debugging Log
            return data
        else:
            st.error(f"API Error: {response.status_code}")
            return None
    except requests.exceptions.Timeout:
        st.error("❌ API Request Timed Out. Try again later.")
        return None
    except requests.exceptions.RequestException as e:
        st.error(f"❌ Network Error: {e}")
        return None

data = fetch_data()

if data:
    df = pd.DataFrame(data)
    st.write("### Raw API Response")
    st.dataframe(df)

    st.write("### Extracted Columns:")
    st.write(df.columns.tolist())
else:
    st.warning("⚠️ No data received from API.")
