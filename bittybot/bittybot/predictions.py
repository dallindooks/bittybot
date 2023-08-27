import datetime
import json
import os
import pickle
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
    
    column_mapping = {
    'h': "High",
    "o": "Open",
    "l": "Low",
    "c": "Close",
    "v": "Volume_(BTC)",
    't': 'Timestamp'
    }
    
    df = pd.DataFrame(btcData)
    
    df.rename(columns=column_mapping, inplace=True)
    
    df.reset_index(drop=True)
    df.set_index("Timestamp", inplace=True)
    df.index = pd.to_datetime(df.index, format='%Y-%m-%dT%H:%M:%SZ')
    
    df["next_minute"] = df["Close"].shift(-1)
    df['Up'] = (df["Close"] < df["next_minute"]).astype(int)
    df = df.dropna()
    df = df.sort_values(by='Timestamp', ascending=True)
    return df

def getRollingAvgs(data):
    horizons = [1,2,3,4,5,6,7,8,9,10]

    global predictors
    predictors = []
    for horizon in horizons:
        rolling_averages = data.rolling(horizon).mean()
        
        ratio_column = f"Close_Ratio_{horizon}"
        data[ratio_column] = data["Close"] / rolling_averages["Close"]
        
        trend_column = f"Trend_{horizon}"
        
        data[trend_column] = data.shift(1).rolling(horizon).sum()["Up"]
        predictors += [ratio_column, trend_column]
        
    return data[-10:]

def makePrediction():
    
    data = getCurrentBTC()
    data = getRollingAvgs(data)
    modelLink = os.environ.get('CURRENT_MODEL')
    
    with open(modelLink, 'rb') as file:
        model = pickle.load(file)
        
    preds = model.predict_proba(data[predictors])[:,1]
    
    preds = pd.Series(preds, index=data.index, name="Predictions")
    return preds.iloc[[-1]]
    