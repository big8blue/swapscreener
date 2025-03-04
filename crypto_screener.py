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

        if isinstance(data, list):  # Ensure response is a list
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
            st.error("Unexpected API response format!")
            return pd.DataFrame()

    except Exception as e:
        st.error(f"Exception: {e}")
        return pd.DataFrame()

# Streamlit UI
st.title("📊 CoinDCX Futures Screener")
st.write("Real-time futures data from CoinDCX.")

while True:
    df = fetch_futures_data()
    
    if not df.empty:
        # Display Data in Columns
        num_cols = 3  # Number of columns
        cols = st.columns(num_cols)

        for i, row in df.iterrows():
            with cols[i % num_cols]:  # Distribute across columns
                st.metric(label=row["Pair"], value=row["LTP"], delta=row["Updated Time"])
    
    time.sleep(refresh_rate)  # Refresh based on user input
    st.rerun()  # Rerun script to update data
