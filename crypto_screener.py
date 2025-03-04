import streamlit as st
import requests
import pandas as pd

# API Endpoints
MARKETS_DETAILS_URL = "https://api.coindcx.com/exchange/v1/markets_details"
TICKER_URL = "https://api.coindcx.com/market_data/ticker"

st.set_page_config(page_title="Crypto Futures LTP", layout="wide")
st.title("🚀 Active Crypto Futures and Their Last Traded Prices")

# Sidebar for refresh rate
refresh_rate = st.sidebar.slider("Refresh Rate (Seconds)", 10, 300, 60)

@st.cache_data(ttl=refresh_rate)
def fetch_markets_details():
    """Fetch details of all markets from CoinDCX API."""
    try:
        response = requests.get(MARKETS_DETAILS_URL, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        st.error(f"Error fetching markets details: {e}")
        return None

@st.cache_data(ttl=refresh_rate)
def fetch_ticker_data():
    """Fetch ticker data for all markets from CoinDCX API."""
    try:
        response = requests.get(TICKER_URL, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        st.error(f"Error fetching ticker data: {e}")
        return None

# Fetch data
markets_details = fetch_markets_details()
ticker_data = fetch_ticker_data()

if markets_details and ticker_data:
    # Filter for active futures markets
    futures_markets = [
        market for market in markets_details.values()
        if market.get('contract_type') == 'futures' and market.get('status') == 'active'
    ]

    if futures_markets:
        # Create DataFrame for futures markets
        futures_df = pd.DataFrame(futures_markets)
        futures_df = futures_df[['symbol', 'base_currency_short_name', 'target_currency_short_name']]
        futures_df.rename(columns={
            'symbol': 'Symbol',
            'base_currency_short_name': 'Base Currency',
            'target_currency_short_name': 'Quote Currency'
        }, inplace=True)

        # Create a dictionary for quick lookup of LTP
        ltp_dict = {item['market']: item['last_price'] for item in ticker_data}

        # Map LTP to each futures symbol
        futures_df['LTP'] = futures_df['Symbol'].map(ltp_dict)

        # Display the DataFrame
        st.write("### Active Futures and Their Last Traded Prices")
        st.dataframe(futures_df)
    else:
        st.warning("No active futures markets found.")
else:
    st.error("Failed to retrieve data from CoinDCX API.")
