import streamlit as st
import ccxt
import pandas as pd
import numpy as np
import requests

# Set Streamlit page title
st.set_page_config(page_title="Crypto Screener", layout="wide")

# Connect to OKX API (No API key needed)
exchange = ccxt.okx()

# Telegram Bot Setup
TELEGRAM_BOT_TOKEN = "YOUR_BOT_TOKEN"
TELEGRAM_CHAT_ID = "YOUR_CHAT_ID"

# Function to send Telegram alerts
def send_telegram_alert(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {"chat_id": TELEGRAM_CHAT_ID, "text": message}
    try:
        requests.post(url, json=payload)
    except Exception as e:
        print("Error sending Telegram message:", e)

# Function to fetch OHLCV data
def get_ohlcv(symbol, timeframe='1m', limit=100):
    try:
        data = exchange.fetch_ohlcv(symbol, timeframe, limit=limit)
        df = pd.DataFrame(data, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
        return df
    except Exception as e:
        st.error(f"Error fetching {symbol}: {e}")
        return None

# Calculate RSI
def calculate_rsi(data, period=14):
    delta = data['close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))

# Calculate EMA
def calculate_ema(data, period=21):
    return data['close'].ewm(span=period, adjust=False).mean()

# Detect Engulfing Candles
def check_engulfing(df):
    if len(df) < 2:
        return False
    prev = df.iloc[-2]
    current = df.iloc[-1]
    return (current['close'] > prev['open'] and current['open'] < prev['close']) or \
           (current['close'] < prev['open'] and current['open'] > prev['close'])

# Check Volume Spikes
def check_volume_spike(df, threshold=2.0):
    avg_volume = df['volume'].rolling(window=10).mean()
    latest_volume = df['volume'].iloc[-1]
    return latest_volume > avg_volume.iloc[-1] * threshold

# Streamlit App UI
st.title("📈 Crypto Screener (OKX)")

# Select timeframes and pairs
timeframe = st.selectbox("Select Timeframe", ['1m', '5m', '15m', '1h', '4h', '1d'])
crypto_pairs = ['BTC-USDT-SWAP', 'ETH-USDT-SWAP', 'SOL-USDT-SWAP', 'XRP-USDT-SWAP']
selected_pairs = st.multiselect("Select Crypto Pairs", crypto_pairs, default=crypto_pairs)

# Run Screener
if st.button("Run Screener"):
    st.write("🔄 Fetching real-time data...")
    results = []
    
    for symbol in selected_pairs:
        df = get_ohlcv(symbol, timeframe)
        if df is None or len(df) < 20:
            continue
        
        df['RSI'] = calculate_rsi(df)
        df['EMA_21'] = calculate_ema(df)
        
        engulfing = check_engulfing(df)
        volume_spike = check_volume_spike(df)
        latest_rsi = df['RSI'].iloc[-1]
        latest_price = df['close'].iloc[-1]

        # Store results
        results.append({
            'Symbol': symbol,
            'Price': round(latest_price, 2),
            'RSI': round(latest_rsi, 2),
            'EMA_21': round(df['EMA_21'].iloc[-1], 2),
            'Engulfing': "✅" if engulfing else "❌",
            'Volume Spike': "✅" if volume_spike else "❌"
        })

        # Send Telegram Alert
        if engulfing or volume_spike:
            alert_msg = f"🚨 Signal Detected 🚨\nSymbol: {symbol}\nPrice: {latest_price}\nRSI: {latest_rsi}\nEngulfing: {engulfing}\nVolume Spike: {volume_spike}"
            send_telegram_alert(alert_msg)
    
    if results:
        df_results = pd.DataFrame(results)
        st.dataframe(df_results, use_container_width=True)
    else:
        st.warning("No data found! Try again later.")
