import streamlit as st
import requests
import pandas as pd
import time
import hashlib
import hmac
import json
import os
from dotenv import load_dotenv

# Load API keys from .env file
load_dotenv()
API_KEY = os.getenv("COINDCX_API_KEY")
SECRET_KEY = os.getenv("COINDCX_SECRET_KEY")

# CoinDCX API endpoints
FUTURES_API_URL = "https://api.coindcx.com/exchange/v1/futures_ticker"

# Function to create signature
def generate_signature(body):
    return hmac.new(SECRET_KEY.encode(), json.dumps(body).encode(), hashlib.sha256).hexdigest()

# Function to fetch real-time futures data
def fetch_futures_data():
    payload = {}
    signature = generate_signature(payload)

    headers = {
        "X-AUTH-APIKEY": API_KEY,
        "X-AUTH-SIGNATURE": signature,
        "Content-Type": "application/json"
    }

    response = requests.post(FUTURES_API_URL, json=payload, headers=headers)
    
    if response.status_code == 200:
        return response.json()
    else:
        st.error("⚠️ API Error: Unable to fetch data")
        return []

# Streamlit UI
st.title("📊 Real-Time CoinDCX Futures Screener")

# User selects refresh rate
refresh_rate = st.sidebar.slider("Refresh Rate (seconds)", 1, 10, 3)

# Data Processing
while True:
    futures_data = fetch_futures_data()
    if not futures_data:
        time.sleep(refresh_rate)
        st.rerun()

    # Convert data to DataFrame
    df = pd.DataFrame(futures_data)

    # Display only relevant columns
    df = df[['symbol', 'last_price', 'high', 'low', 'volume', 'change_24h']]
    
    # Display Table
    st.dataframe(df)

    # Refresh data at the selected interval
    time.sleep(refresh_rate)
    st.rerun()
