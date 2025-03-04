import streamlit as st
import requests
import pandas as pd
from datetime import datetime, timedelta

# ✅ Correct CoinDCX API URL
API_URL = "https://api.coindcx.com/exchange/v1/derivatives/futures/data/active_instruments"

# ✅ Set Page Configuration
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

# ✅ Function to Fetch Data (Auto Refresh)
@st.cache_data(ttl=refresh_rate)
def fetch_data():
    """Fetch active futures data from CoinDCX API and handle API structure."""
    try:
        response = requests.get(API_URL)
        data = response.json()

        if not isinstance(data, list):  # Ensure response is a list
            st.error("Invalid API response format")
            return pd.DataFrame()

        df = pd.DataFrame(data)

        # ✅ Print available columns for debugging
        st.write("Available Columns:", df.columns.tolist())

        # ✅ Check if required columns exist
        if not {"symbol", "mark_price", "volume", "timestamp"}.issubset(df.columns):
            st.error("Missing expected columns in API response")
            return pd.DataFrame()

        # ✅ Select relevant columns
        df = df[["symbol", "mark_price", "volume", "timestamp"]]
        df.columns = ["Symbol", "Price", "Volume", "Timestamp"]
        
        df["Price"] = df["Price"].astype(float)
        df["Volume"] = df["Volume"].astype(float) / 1_000_000  # Convert to Millions (M)
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

# ✅ Display Table
placeholder = st.empty()

def update_data():
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

# ✅ Run update_data() once on launch
update_data()
