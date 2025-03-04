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

        if isinstance(data, list) and len(data) > 0:
            df = pd.DataFrame([
                {
                    "Pair": item.get("symbol", "N/A"),
                    "LTP": item.get("last_price", "N/A"),
                    "Updated Time": time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
                }
                for item in data if isinstance(item, dict)
            ])
            return df
        else:
            st.error("❌ API response is empty or incorrect format!")
            return pd.DataFrame()

    except Exception as e:
        st.error(f"❌ Exception: {e}")
        return pd.DataFrame()

# Streamlit UI
st.title("📊 CoinDCX Futures Screener")
st.write("Real-time futures data from CoinDCX.")

while True:
    df = fetch_futures_data()
    
    if not df.empty:
        with st.container():  # Use container to ensure display
            for index, row in df.iterrows():
                st.write(f"**{row['Pair']}** - LTP: {row['LTP']} (Updated: {row['Updated Time']})")
    
    time.sleep(refresh_rate)  # Wait before refreshing
    st.experimental_rerun()  # Refresh app to update data
