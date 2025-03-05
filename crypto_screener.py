@sio.on('currentPrices@futures#update')
def on_message(response):
  print(response["data"])
    
