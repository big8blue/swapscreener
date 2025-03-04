import streamlit as st
import requests
import pandas as pd
import time
from datetime import datetime, timedelta

# CoinDCX API Endpoints
MARKETS_URL = "https://api.coindcx.com/exchange/v1/markets"
CANDLES_URL = "https://public.coindcx.com/market_data/candles"
API_KEY = "64fcb132c957dbfc1fd4db8f96d9cf69fb39684333abee29"
HEADERS = {"Authorization": f"Bearer {API_KEY}"}

# Streamlit Page Configuration
st.set_page_config(page_title="🚀 Crypto Futures Screener", layout="wide")
st.title("📊 CoinDCX Real-Time Futures Screener")

# Sidebar Filters
st.sidebar.header("🔍 Filters")

# Volume Range Filter
st.sidebar.subheader("📊 Volume Range (Millions)")
col1, col2 = st.sidebar.columns(2)
min_volume = col1.number_input("Min Volume (M)", min_value=0.0, max_value=1000.0, value=0.5, step=0.1)
max_volume = col2.number_input("Max Volume (M)", min_value=0.0, max_value=1000.0, value=50.0, step=0.1)

# Refresh Rate
refresh_rate = st.sidebar.slider("⏳ Refresh Rate (Seconds)", 1, 10, 1)

# Function to Fetch Futures Markets
def get_futures_markets():
    """Fetch all available futures markets from CoinDCX."""
    try:
        response = requests.get(MARKETS_URL, headers=HEADERS)
        if response.status_code != 200:
            st.error(f"API Error: {response.status_code} - {response.text}")
            return []

        data = response.json()
        
        # Ensure correct format
        if isinstance(data, dict) and "markets" in data:
            data = data["markets"]

        if not isinstance(data, list):
            st.error("Unexpected API response format.")
            return []

        # Filter only futures markets
        futures_markets = [m["market"] for m in data if isinstance(m, dict) and 'FUTURES' in m.get('market', '')]
        return futures_markets
    except Exception as e:
        st.error(f"Error fetching futures markets: {e}")
        return []

# Function to Fetch Futures Data
def fetch_futures_data():
    """Fetch futures volume data for each symbol."""
    futures_symbols = get_futures_markets()
    if not futures_symbols:
        return pd.DataFrame()

    results = []
    for symbol in futures_symbols:
        try:
            response = requests.get(CANDLES_URL, params={"symbol": symbol, "interval": "1m", "limit": 1}, headers=HEADERS)
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, list) and data:
                    results.append({"Symbol": symbol, "Volume": float(data[0]["volume"])})
        except Exception as e:
            st.warning(f"Error fetching {symbol}: {e}")

    df = pd.DataFrame(results)

    # Convert Volume to Millions (M)
    df["Volume"] = df["Volume"] / 1_000_000
    df = df[(df["Volume"] >= min_volume) & (df["Volume"] <= max_volume)]
    
    return df.sort_values(by="Volume", ascending=False)

# UI Placeholder for Live Updates
placeholder = st.empty()

# Live Update Function
def update_data():
    df = fetch_futures_data()
    if not df.empty:
        with placeholder.container():
            st.dataframe(df, use_container_width=True)
    else:
        st.warning("No data available. Check API status.")

# Auto-refresh Loop
while True:
    update_data()
    time.sleep(refresh_rate)
