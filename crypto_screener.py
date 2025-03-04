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
        data = response.json()

        # Print API response to inspect structure
        st.write("API Response:", data)

        if isinstance(data, list):  # Ensure response is a list of dictionaries
            df = pd.DataFrame([
                {
                    "Pair": item.get("symbol", "N/A"),  # Adjust based on actual key names
                    "LTP": item.get("last_price", "N/A"),
                    "Updated Time": time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
                }
                for item in data if isinstance(item, dict)  # Ensure item is a dictionary
            ])
            return df
        else:
            st.error("Unexpected API response format!")
            return pd.DataFrame()

    except Exception as e:
        st.error(f"Exception: {e}")
        return pd.DataFrame()

st.title("CoinDCX Crypto Futures Screener")
st.write("Displaying real-time futures data from CoinDCX.")

df = fetch_futures_data()
if not df.empty:
    st.dataframe(df)
