import os
from alpaca.data.requests import CryptoBarsRequest
from alpaca.data.timeframe import TimeFrame
from alpaca.data.live import CryptoDataStream
import requests

API_KEY = os.getenv("API-KEY")
SECRET_KEY = os.getenv("SECRET-KEY")

baseURL = "https://paper-api.alpaca.markets"
accountURL = "{}/v2/account".format(baseURL)

btcBarsURL = "https://data.alpaca.markets/v1beta3/crypto/us/latest/bars"

r = requests.get(btcBarsURL, headers={'APCA-API-KEY-ID': API_KEY, 'APCA-API-SECRET-KEY': SECRET_KEY}, params={"symbols":"BTC/USD"})

print(r.content)

