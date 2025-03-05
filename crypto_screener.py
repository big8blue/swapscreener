import socketio
import json
import time

# CoinDCX WebSocket Endpoint
socketEndpoint = 'wss://stream.coindcx.com'

# Initialize SocketIO Client
sio = socketio.Client(reconnection=True, reconnection_attempts=5, logger=True, engineio_logger=True)

# Event: Connection Established
@sio.event
def connect():
    print("✅ Successfully connected to CoinDCX WebSocket!")

# Event: Connection Error
@sio.event
def connect_error(data):
    print("❌ Connection failed. Retrying...")

# Event: Disconnected
@sio.event
def disconnect():
    print("🔴 Disconnected from WebSocket. Reconnecting in 5s...")
    time.sleep(5)
    sio.connect(socketEndpoint, transports=['websocket'])

# Subscribe to Futures Price Updates
@sio.on('currentPrices@futures#update')
def on_message(response):
    try:
        data = response.get("data", [])
        if data:
            print("📊 Real-Time Futures Prices:", data)
        else:
            print("⚠️ No price data received!")
    except Exception as e:
        print(f"🚨 Error processing message: {e}")

# Connect and Start Listening
try:
    sio.connect(socketEndpoint, transports=['websocket'])
    sio.wait()
except KeyboardInterrupt:
    print("❌ WebSocket connection closed by user.")
    sio.disconnect()
