import streamlit as st
import requests
import pandas as pd

# API to get futures symbols
SYMBOLS_API = "https://api.coindcx.com/exchange/v1/derivatives/futures/data/active_instruments"
# API to fetch real-time LTP prices
LTP_API = "https://public.coindcx.com/market_data/v3/current_prices/futures/rt"

st.set_page_config(page_title="Crypto Screener", layout="wide")
st.title("🚀 Real-Time Crypto Futures Screener")

st.sidebar.header("🔍 Filters")
refresh_rate = st.sidebar.slider("Refresh Rate (Seconds)", 1, 10, 1)

@st.cache_data(ttl=refresh_rate)
def fetch_symbols():
    """Fetch futures instrument symbols."""
    try:
        response = requests.get(SYMBOLS_API)
        data = response.json()

        if isinstance(data, list):
            return [item["symbol"] for item in data if "symbol" in item]
        else:
            st.error("Unexpected API response format.")
            return None
    except Exception as e:
        st.error(f"Error fetching symbols: {e}")
        return None



# Fetch symbols and LTP data
symbols = fetch_symbols()

if symbols and ltp_data:
    # Create DataFrame
    df = pd.DataFrame(symbols, columns=["symbol"])
    df["LTP"] = df["symbol"].map(ltp_data)

    st.write("### Real-Time Futures Data")
    st.dataframe(df)
else:
    st.error("Failed to fetch complete data. Check API responses.")
