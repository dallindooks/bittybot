from rest_framework import status
from rest_framework.response import Response
import os
import dotenv
import requests
from dotenv import load_dotenv

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
    
    if (predValue > .55):
        return buyBTC()
    elif (predValue < .4):
        return sellBTC()
    
def buyBTC():
    
    global tradeUrl
    # print(amount)
    
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
        
        buyCallResponse = requests.post(tradeUrl, json=payload, headers=headers)
        buyCallResponse.raise_for_status()
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
