import streamlit as st
import asyncio
import aiohttp
import pandas as pd

# CoinDCX API Endpoints
MARKETS_URL = "https://api.coindcx.com/exchange/v1/markets"
CANDLES_URL = "https://public.coindcx.com/market_data/candles"
TIMEFRAMES = ["1m", "5m", "15m"]

# Function to fetch all futures pairs
async def get_futures_symbols():
    async with aiohttp.ClientSession() as session:
        async with session.get(MARKETS_URL) as response:
            markets = await response.json()
            return [m["market"] for m in markets if "FUTURES" in m["market"]]

# Function to fetch candlestick data
async def fetch_data(session, symbol, timeframe):
    params = {"symbol": symbol, "interval": timeframe, "limit": 1}
    async with session.get(CANDLES_URL, params=params) as response:
        data = await response.json()
        if data:
            return {"Symbol": symbol, "Timeframe": timeframe, "Volume": data[0]["volume"]}
        return None

# Main function to fetch data for all futures symbols
async def fetch_futures_data():
    symbols = await get_futures_symbols()
    async with aiohttp.ClientSession() as session:
        tasks = [fetch_data(session, symbol, tf) for symbol in symbols for tf in TIMEFRAMES]
        results = await asyncio.gather(*tasks)
        return [res for res in results if res]

# Streamlit UI
async def main():
    st.title("📊 CoinDCX Futures Screener")
    st.write("Tracks real-time volume across all futures pairs and multiple timeframes.")

    with st.spinner("Fetching data..."):
        data = await fetch_futures_data()
    
    if data:
        df = pd.DataFrame(data)
        st.dataframe(df, use_container_width=True)

# Run Streamlit
asyncio.run(main())
