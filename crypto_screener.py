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
    # Convert response to DataFrame
    df = pd.DataFrame(data)

    # Display raw data to analyze structure
    st.write("### Raw API Response in Table")
    st.dataframe(df)

    # Automatically detect available columns
    st.write("### Extracted Columns:")
    st.write(df.columns.tolist())

    # Display structured data (if valid columns exist)
    if not df.empty and len(df.columns) > 1:
        st.write("### Processed Data Table")
        st.dataframe(df)
    else:
        st.warning("API response does not contain expected structured data.")
