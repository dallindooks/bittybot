from rest_framework import status
from rest_framework.response import Response
import os
import dotenv
import requests
from dotenv import load_dotenv
from .firebase import getDb

dotenv.load_dotenv()
accountUrl = os.environ.get('GET_ACCOUNT_URL')
tradeUrl = os.environ.get('CREATE_ORDER_URL')
test = os.environ.get('CURRENT_MODEL')
apiKey = os.environ.get("API_KEY")
secretKey = os.environ.get("SECRET_KEY")
btcPosURL = os.environ.get("BTC_POSITION_URL")


def evaluatePrediction(prediction):
    date = prediction.keys()
    
    predValue = prediction[0]
    
    last_trade = getLastTradeData()
    
    if (predValue > .525):
        return buyBTC()
    elif (predValue < .475):
        return sellBTC()
    else: 
        return sellBTC if last_trade["side"] == "sell" else buyBTC()
    
def buyBTC():
    
    global tradeUrl
    
    try:
        cash = float(getCurrentCash())
        amount = round(cash * 0.05, 2 )
        
        payload = {
            "side": "buy",
            "type": "market",
            "time_in_force": "ioc",
            "symbol": "BTC/USD",
            "notional": amount
            }

        headers = {
                "accept": "application/json",
                "content-type": "application/json",
                "APCA-API-KEY-ID": apiKey,
                "APCA-API-SECRET-KEY": secretKey
        }
        
        buyCallResponse = requests.post(tradeUrl, json=payload, headers=headers)
        
        buyCallResponse.raise_for_status()
        
        logTradeData(buyCallResponse)
        
        return Response("BTC Bought ", status=status.HTTP_200_OK)
    
    except requests.exceptions.RequestException as e:
        print("Request error:", e)

def sellBTC():
    global btcPosURL
    
    try:
        cash = getCurrBTCPosition()
        amount = round(cash * 0.05, 2 )
        
        payload = {
            "side": "sell",
            "type": "market",
            "time_in_force": "ioc",
            "symbol": "BTC/USD",
            "notional": amount
            }

        headers = {
                "accept": "application/json",
                "content-type": "application/json",
                "APCA-API-KEY-ID": apiKey,
                "APCA-API-SECRET-KEY": secretKey
        }
        
        sellCallResponse = requests.post(tradeUrl, json=payload, headers=headers)
        
        sellCallResponse.raise_for_status()
        
        logTradeData(sellCallResponse)
        
        return Response("BTC Sold ", status=status.HTTP_200_OK)
    
    except requests.exceptions.RequestException as e:
        print("Request error:", e)

def getCurrentCash():

    global accountUrl
    global secretKey
    global apiKey

    r = requests.get(
    accountUrl,
    headers={"APCA-API-KEY-ID": apiKey, "APCA-API-SECRET-KEY": secretKey},
    ).json()
    
    cash = r['cash']
    
    return cash

def getCurrBTCPosition():
    
    global btcPosURL
    global secretKey
    global apiKey
    
    r = requests.get(
    btcPosURL,
    headers={"APCA-API-KEY-ID": apiKey, "APCA-API-SECRET-KEY": secretKey},
    ).json()
    
    quantity = float(r['qty'])
    price = float(r['current_price'])
    
    cash = quantity * price
    
    return round(cash, 2)

def logTradeData(response):
    json_response = response.json()
    
    dollarAmount = json_response["notional"]
    timeSubmitted = json_response["submitted_at"]
    side = json_response["side"]
    
    data = {
        "quantity" : dollarAmount,
        "time" : timeSubmitted,
        "side" : side
    }
    
    db = getDb()
    
    db.child("trades").push(data)
    
def getLastTradeData():
    
    db = getDb()
    trades_ref = db.child("trades")
    
    data = trades_ref.get().val()
    
    keys = list(data.keys())
    
    last_key = keys[-1]
    
    last_entry = data[last_key]
    
    return last_entry
    