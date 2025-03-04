import streamlit as st
import requests
import pandas as pd
import time
from datetime import datetime, timedelta

# ✅ Corrected CoinDCX API URL
API_URL = "https://api.coindcx.com/exchange/v1/derivatives/futures/data/active_instruments"

# ✅ Streamlit Page Configuration
st.set_page_config(page_title="Crypto Screener", layout="wide")

st.title("🚀 Real-Time Crypto Futures Screener")

# ✅ Sidebar Filters
st.sidebar.header("🔍 Filters")

# ✅ Volume Range Input
st.sidebar.subheader("📊 Volume Range (in Millions)")
col1, col2 = st.sidebar.columns(2)
min_volume_input = col1.number_input("Min Volume (M)", min_value=0.0, max_value=1000.0, value=0.5, step=0.1)
max_volume_input = col2.number_input("Max Volume (M)", min_value=0.0, max_value=1000.0, value=50.0, step=0.1)

# ✅ Volume Range Slider
min_volume, max_volume = st.sidebar.slider(
    "Or use the slider below",
    min_value=0.0,
    max_value=1000.0,
    value=(min_volume_input, max_volume_input),
    step=0.1
)

# ✅ Refresh Rate Selection
refresh_rate = st.sidebar.slider("Refresh Rate (Seconds)", 1, 10, 1)

# ✅ Function to Fetch Data (No caching for real-time updates)
def fetch_data():
    """Fetch all active futures data from CoinDCX API."""
    try:
        response = requests.get(API_URL)
        data = response.json()

        if not data:
            return pd.DataFrame()

        df = pd.DataFrame(data)

        # ✅ Adjust column names to match API response
        df = df[["symbol", "mark_price", "volume", "timestamp"]]  # ✅ Ensure correct column names
        df.columns = ["Symbol", "Price", "Volume", "Timestamp"]
        df["Price"] = df["Price"].astype(float)
        df["Volume"] = df["Volume"].astype(float) / 1_000_000  # Convert volume to Millions (M)
        df["Timestamp"] = pd.to_datetime(df["Timestamp"], unit="ms")

        # ✅ Filter for USDT futures
        df = df[df["Symbol"].str.endswith("_USDT")]

        return df

    except Exception as e:
        st.error(f"Error fetching data: {e}")
        return pd.DataFrame()

# ✅ Convert UTC to IST
def convert_to_ist(utc_time):
    ist_time = utc_time + timedelta(hours=5, minutes=30)
    return ist_time.strftime("%I:%M:%S %p")

# ✅ Live Updates with Auto Refresh
placeholder = st.empty()

# ✅ Streamlit auto-refresh mechanism (removes infinite loop)
while True:
    df = fetch_data()

    if not df.empty:
        df["Updated Time (IST)"] = df["Timestamp"].apply(convert_to_ist)
        df = df.drop(columns=["Timestamp"])

        # ✅ Apply min & max volume filter
        df = df[(df["Volume"] >= min_volume) & (df["Volume"] <= max_volume)]

        # ✅ Format Volume
        df["Volume"] = df["Volume"].apply(lambda x: f"{x:.2f}M")

        # ✅ Display Data
        with placeholder.container():
            st.dataframe(df.sort_values(by="Price", ascending=False), height=600)

    time.sleep(refresh_rate)  # ✅ Refresh at user-selected interval
    st.experimental_rerun()  # ✅ Properly updates Streamlit UI
