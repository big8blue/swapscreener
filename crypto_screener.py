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
        response = requests.get(API_URL)
        data = response.json()  # Convert response to JSON

        # Ensure response is a list
        if isinstance(data, list):
            return data
        else:
            st.error("Unexpected API response format")
            return None

    except Exception as e:
        st.error(f"Error fetching data: {e}")
        return None

data = fetch_data()

if data:
    # Convert the list of dictionaries to a DataFrame
    df = pd.DataFrame(data)

    # Display the first few rows
    st.write("### API Data in Table Format")
    st.dataframe(df)

    # Extract specific columns if available
    expected_columns = ["symbol", "mark_price", "volume", "timestamp"]
    available_columns = [col for col in expected_columns if col in df.columns]

    if available_columns:
        df_filtered = df[available_columns]

        # Convert timestamp if available
        if "timestamp" in df_filtered.columns:
            df_filtered["timestamp"] = pd.to_datetime(df_filtered["timestamp"], unit='ms')

        st.write("### Processed Data")
        st.dataframe(df_filtered)

    else:
        st.error("Expected columns are missing from API response")
