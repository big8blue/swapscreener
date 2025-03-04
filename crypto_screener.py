import streamlit as st
import requests
import pandas as pd

# CoinDCX API Endpoints
MARKETS_URL = "https://api.coindcx.com/exchange/v1/markets"
CANDLES_URL = "https://public.coindcx.com/market_data/candles"

# Fetch Futures Markets
def get_futures_markets():
    response = requests.get(MARKETS_URL)
    markets = response.json()
    futures_markets = [market for market in markets if 'FUTURES' in market['market']]
    return futures_markets

# Fetch Candlestick Data
def get_candlestick_data(symbol, interval='1m', limit=1):
    params = {'symbol': symbol, 'interval': interval, 'limit': limit}
    response = requests.get(CANDLES_URL, params=params)
    return response.json()

# Streamlit App
st.title("CoinDCX Futures Screener")

# Fetch and Display Data
markets = get_futures_markets()
data = []
for market in markets:
    symbol = market['market']
    candles = get_candlestick_data(symbol)
    if candles:
        latest_candle = candles[0]
        data.append({
            'Symbol': symbol,
            'Time': latest_candle['time'],
            'Open': latest_candle['open'],
            'High': latest_candle['high'],
            'Low': latest_candle['low'],
            'Close': latest_candle['close'],
            'Volume': latest_candle['volume']
        })

df = pd.DataFrame(data)
st.dataframe(df)
