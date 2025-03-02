import streamlit as st
import requests
import pandas as pd
import time

API_URL = "https://www.okx.com/api/v5/market/tickers?instType=SWAP"

st.set_page_config(page_title="Crypto Futures Screener", layout="wide")
st.title("🚀 Real-Time Crypto Futures Screener")

# Store historical prices
if "prev_prices" not in st.session_state:
    st.session_state.prev_prices = {}

@st.cache_data(ttl=10)  # Cache data for 10 seconds
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

def calculate_5m_change(df):
    changes = []
    for index, row in df.iterrows():
        symbol = row["Symbol"]
        current_price = float(row["Price (USDT)"])

        # Fetch previous price
        prev_price = st.session_state.prev_prices.get(symbol, current_price)

        # Calculate change
        price_change = ((current_price - prev_price) / prev_price) * 100 if prev_price else 0
        changes.append(f"{price_change:.2f}%")

        # Update stored prices
        st.session_state.prev_prices[symbol] = current_price

    df["5m Change (%)"] = changes
    return df

st_autorefresh = st.empty()

while True:
    df = fetch_data()
    df = calculate_5m_change(df)
    st_autorefresh.dataframe(df, height=600)
    time.sleep(1)  # Refresh every second
