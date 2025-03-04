import streamlit as st
import requests
import pandas as pd
import time
import asyncio
from datetime import datetime, timedelta

# CoinDCX API for Futures Market
MARKETS_URL = "https://api.coindcx.com/exchange/v1/markets"
CANDLES_URL = "https://public.coindcx.com/market_data/candles"

# API Key (Replace with your own API key)
API_KEY = "64fcb132c957dbfc1fd4db8f96d9cf69fb39684333abee29"
HEADERS = {"Authorization": f"Bearer {API_KEY}"}

# Set Page Configuration
st.set_page_config(page_title="Crypto Screener", layout="wide")

st.title("🚀 CoinDCX Real-Time Crypto Futures Screener")

# Sidebar Filters
st.sidebar.header("🔍 Filters")

# Volume Range Input
st.sidebar.subheader("📊 Volume Range (in Millions)")
col1, col2 = st.sidebar.columns(2)
min_volume_input = col1.number_input("Min Volume (M)", min_value=0.0, max_value=1000.0, value=0.5, step=0.1)
max_volume_input = col2.number_input("Max Volume (M)", min_value=0.0, max_value=1000.0, value=50.0, step=0.1)

# Slider for convenience
min_volume, max_volume = st.sidebar.slider(
    "Or use the slider below",
    min_value=0.0,
    max_value=1000.0,
    value=(min_volume_input, max_volume_input),
    step=0.1
)

# Refresh Rate
refresh_rate = st.sidebar.slider("Refresh Rate (Seconds)", 1, 10, 1)

# Caching API Calls (refreshes every X seconds)
@st.cache_data(ttl=refresh_rate)
def get_futures_symbols():
    """Fetch all futures pairs from CoinDCX API."""
    try:
        response = requests.get(MARKETS_URL, headers=HEADERS)
        data = response.json()
        if not data:
            return []
        return [m["market"] for m in data if "FUTURES" in m["market"] and m["market"].endswith("USDTFUT")]
    except Exception as e:
        st.error(f"Error fetching futures symbols: {e}")
        return []

async def fetch_volume(session, symbol):
    """Fetch the latest volume for a given futures pair."""
    params = {"symbol": symbol, "interval": "1m", "limit": 1}
    try:
        async with session.get(CANDLES_URL, headers=HEADERS, params=params) as response:
            if response.status == 200:
                data = await response.json()
                if isinstance(data, list) and data:
                    return {"Symbol": symbol, "Volume": data[0]["volume"]}
    except Exception as e:
        print(f"Error fetching {symbol} volume: {e}")
    return None

async def fetch_data():
    """Fetch volume data for all futures symbols."""
    symbols = get_futures_symbols()
    if not symbols:
        return pd.DataFrame()

    async with aiohttp.ClientSession() as session:
        tasks = [fetch_volume(session, symbol) for symbol in symbols]
        results = await asyncio.gather(*tasks)
    
    data = [res for res in results if res]
    if not data:
        return pd.DataFrame()
    
    df = pd.DataFrame(data)
    df["Volume"] = df["Volume"].astype(float) / 1_000_000  # Convert to Millions (M)
    return df

# Convert UTC to IST
def convert_to_ist():
    ist_time = datetime.utcnow() + timedelta(hours=5, minutes=30)
    return ist_time.strftime("%I:%M:%S %p")

# Live Updates with Auto Refresh
placeholder = st.empty()

def update_data():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    df = loop.run_until_complete(fetch_data())

    if not df.empty:
        df["Updated Time (IST)"] = convert_to_ist()

        # Apply volume filter
        df = df[(df["Volume"] >= min_volume) & (df["Volume"] <= max_volume)]

        # Convert Volume to readable format (M)
        df["Volume"] = df["Volume"].apply(lambda x: f"{x:.2f}M")

        # Display Data
        with placeholder.container():
            st.dataframe(df.sort_values(by="Volume", ascending=False), height=600)
    else:
        st.warning("No data available. Please check API status.")

while True:
    update_data()
    time.sleep(refresh_rate)  # Refresh based on user input
