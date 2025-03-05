import socketio
import hmac
import hashlib
import json
socketEndpoint = 'wss://stream.coindcx.com'
sio = socketio.Client()

sio.connect(socketEndpoint, transports = 'websocket')

key = "64fcb132c957dbfc1fd4db8f96d9cf69fb39684333abee29"
secret = "53866511d5f015b28cfaac863065eb75f9f0f9e26d5c905f890095604e7ca37d"

# python3
secret_bytes = bytes(secret, encoding='utf-8')
# python2
secret_bytes = bytes(secret)

body = {"channel":"coindcx"}
json_body = json.dumps(body, separators = (',', ':'))
signature = hmac.new(secret_bytes, json_body.encode(), hashlib.sha256).hexdigest()

# Join channel
sio.emit('join', { 'channelName': 'coindcx', 'authSignature': signature, 'apiKey' : key })

### Listen update on eventName
### Replace the <eventName> with the df-position-update, df-order-update, ###balance-update

@sio.on('balance-update')
def on_message(response):
  print(response["data"])
# leave a channel
sio.emit('leave', { 'channelName' : 'coindcx' })
