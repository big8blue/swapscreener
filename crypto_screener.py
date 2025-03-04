import streamlit as st
import requests

API_URL = "https://api.coindcx.com/exchange/v1/derivatives/futures/data/active_instruments"

st.title("Debugging CoinDCX API Response")

# Fetch raw API response
try:
    response = requests.get(API_URL)
    data = response.json()

    # Display full API response
    st.write("Raw API Response:", data)

    # Display first item to check its structure
    if isinstance(data, list) and len(data) > 0:
        st.write("Sample Entry:", data[0])
        st.write("Available Keys:", list(data[0].keys()))
    else:
        st.error("API returned empty or unexpected data structure")

except Exception as e:
    st.error(f"Error fetching data: {e}")
