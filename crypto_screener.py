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
