import datetime
import json
import os
import pickle
from alpaca.data.requests import CryptoBarsRequest
from alpaca.data.timeframe import TimeFrame
from alpaca.data.live import CryptoDataStream
import dotenv
import requests
import pandas as pd
import numpy as np
from dotenv import load_dotenv

API_KEY = os.getenv("API-KEY")
SECRET_KEY = os.getenv("SECRET-KEY")

dotenv.load_dotenv()

baseURL = "https://paper-api.alpaca.markets"
accountURL = "{}/v2/account".format(baseURL)

predictors = []

btcBarsURL = "https://data.alpaca.markets/v1beta3/crypto/us/bars"

r = requests.get(
    btcBarsURL,
    headers={"APCA-API-KEY-ID": API_KEY, "APCA-API-SECRET-KEY": SECRET_KEY},
    params={"symbols": "BTC/USD", "timeframe": "1Min", "sort": "desc"},
)

def getCurrentBTC():
    btcBarsURL = "https://data.alpaca.markets/v1beta3/crypto/us/bars"

    r = requests.get(
    btcBarsURL,
    headers={"APCA-API-KEY-ID": API_KEY, "APCA-API-SECRET-KEY": SECRET_KEY},
    params={"symbols": "BTC/USD", "timeframe": "1Min", "sort": "desc"},
).json()
    
    btcData = r["bars"]["BTC/USD"]
    df = pd.DataFrame(btcData)
    df['t'] = pd.to_datetime(df['t'])
    df.set_index('t', inplace=True)
    df["next_minute"] = df["c"].shift(-1)
    df['Up'] = (df["c"] < df["next_minute"]).astype(int)
    df = df.dropna()
    df = df.sort_values(by='t', ascending=True)
    return df

def getRollingAvgs(data):
    horizons = [1,3,5,20,60]

    for horizon in horizons:
        rolling_averages = data.rolling(horizon).mean()
        
        ratio_column = f"Close_Ratio_{horizon}"
        data[ratio_column] = data["c"] / rolling_averages["c"]
        
        trend_column = f"Trend_{horizon}"
        
        data[trend_column] = data.shift(1).rolling(horizon).sum()["Up"]
        global predictors
        predictors += [ratio_column, trend_column]
    return data[-60:]

def makePrediction():
    
    data = getCurrentBTC()
    data = getRollingAvgs(data)
    
    modelLink = os.environ.get('CURRENT_MODEL')
    
    with open(modelLink, 'rb') as file:
        model = pickle.load(file)
        
    model.fit(data[predictors], data["Up"])
    
    with open(modelLink, 'wb') as file:
        pickle.dump(model, file)

    preds = model.predict_proba(data[predictors])[:,1]
    return preds[0]
    
