import streamlit as st
import asyncio
import aiohttp
import pandas as pd

# API Endpoints
MARKETS_URL = "https://api.coindcx.com/exchange/v1/markets"
CANDLES_URL = "https://public.coindcx.com/market_data/candles"
TIMEFRAMES = ["1m", "5m", "15m"]

# Function to fetch all futures pairs
async def get_futures_symbols():
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(MARKETS_URL) as response:
                if response.status == 200:
                    markets = await response.json()
                    return [m["market"] for m in markets if "FUTURES" in m.get("market", "")]
                else:
                    st.error(f"Error fetching markets: {response.status}")
                    return []
        except Exception as e:
            st.error(f"API Error: {e}")
            return []

# Function to fetch candlestick data
async def fetch_data(session, symbol, timeframe):
    params = {"symbol": symbol, "interval": timeframe, "limit": 1}
    try:
        async with session.get(CANDLES_URL, params=params) as response:
            if response.status == 200:
                data = await response.json()
                if isinstance(data, list) and data:
                    return {"Symbol": symbol, "Timeframe": timeframe, "Volume": data[0]["volume"]}
            return None
    except Exception as e:
        print(f"Error fetching {symbol} {timeframe}: {e}")
        return None

# Fetch data for all futures symbols
async def fetch_futures_data():
    symbols = await get_futures_symbols()
    if not symbols:
        return []
    
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
    else:
        st.warning("No data available. Please check API status.")

# Run Streamlit safely
if __name__ == "__main__":
    asyncio.run(main())
