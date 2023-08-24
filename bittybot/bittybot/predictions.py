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

API_KEY = os.getenv("API_KEY")
SECRET_KEY = os.getenv("SECRET_KEY")

dotenv.load_dotenv()

baseURL = "https://paper-api.alpaca.markets"
accountURL = "{}/v2/account".format(baseURL)

predictors = []

btcBarsURL = "https://data.alpaca.markets/v1beta3/crypto/us/bars"

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
    global predictors
    predictors = []
    for horizon in horizons:
        rolling_averages = data.rolling(horizon).mean()
        
        ratio_column = f"Close_Ratio_{horizon}"
        data[ratio_column] = data["c"] / rolling_averages["c"]
        
        trend_column = f"Trend_{horizon}"
        
        data[trend_column] = data.shift(1).rolling(horizon).sum()["Up"]
        predictors += [ratio_column, trend_column]
        
    return data[-60:]

def makePrediction():
    
    data = getCurrentBTC()
    data = getRollingAvgs(data)
    modelLink = os.environ.get('CURRENT_MODEL')
    
    with open(modelLink, 'rb') as file:
        model = pickle.load(file)
        
    preds = model.predict_proba(data[predictors])[:,1]
    
    preds = pd.Series(preds, index=data.index, name="Predictions")
    print(preds)
    
    fiveMinAgo = data.iloc[[-15]]
    model.fit(fiveMinAgo[predictors], fiveMinAgo["Up"])
    
    with open(modelLink, 'wb') as file:
        pickle.dump(model, file)
    return preds.iloc[[-1]]

makePrediction()
    