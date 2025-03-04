import streamlit as st
import requests

API_URL = "https://api.coindcx.com/exchange/v1/derivatives/futures/data/active_instruments"

st.title("Debugging CoinDCX API Response")

# Fetch raw API response
try:
    response = requests.get(API_URL)
    
    # Check if response is JSON or plain text
    if "application/json" in response.headers.get("Content-Type", ""):
        data = response.json()  # Parse JSON
    else:
        data = response.text  # Raw text response

    # Display full API response
    st.write("Raw API Response:", data)

except Exception as e:
    st.error(f"Error fetching data: {e}")
