from datetime import datetime
import time
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
    predValue = prediction[0]
    print(predValue)
    open_buy_tuple = getLastBuy()
    
    if open_buy_tuple:
        if open_buy_tuple[0]["open"] == 1:
            sellBTC(open_buy_tuple)
       
    if (predValue > .45):
        buyBTC(predValue)
        
    
def buyBTC(predValue):
    global tradeUrl
    
    try:
        cash = float(getCurrentCash())
        amount = round(cash * 0.10, 2 )
        
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
        
        buyCallResponse = requests.post(tradeUrl, json=payload, headers=headers).json()
        
        time.sleep(3)
        
        filled_buy = getFilledTrade(buyCallResponse["id"])
        buy_price = float(filled_buy["filled_avg_price"])
        
        data = {
        "id": filled_buy["id"],
        "quantity" : filled_buy["filled_qty"],
        "buy_price": buy_price,
        "buy_time" : filled_buy["filled_at"],
        "side" : filled_buy["side"],
        "open": 1,
        "prediction": predValue
        }
    
        db = getDb()
        
        db.child("buy").push(data)
        print("BTC Bought")
        return Response("BTC Bought ", status=status.HTTP_200_OK)
    
    except requests.exceptions.RequestException as e:
        print("Buy Error:", e)

def sellBTC(open_buy_tuple):
    global btcPosURL
    
    open_buy = open_buy_tuple[0]
    key = open_buy_tuple[1]
    
    try:
        qty = float(open_buy["quantity"])
        buy_price = float(open_buy["buy_price"])
        
        payload = {
            "side": "sell",
            "type": "market",
            "time_in_force": "ioc",
            "symbol": "BTC/USD",
            "qty": qty
            }

        headers = {
                "accept": "application/json",
                "content-type": "application/json",
                "APCA-API-KEY-ID": apiKey,
                "APCA-API-SECRET-KEY": secretKey
        }
        
        sellCallResponse = requests.post(tradeUrl, json=payload, headers=headers).json()
        
        time.sleep(3)
        
        filled_sell = getFilledTrade(sellCallResponse["id"])
        sell_price = float(filled_sell["filled_avg_price"])
        sold_qty = float(filled_sell["qty"])
        
        profitability = (sell_price - buy_price) * sold_qty
        
        data = {
        "id": filled_sell["id"],
        "quantity" : filled_sell["filled_qty"],
        "sell_price": sell_price,
        "buy_price": buy_price,
        "buy_time" : open_buy["buy_time"],
        "sell_time": filled_sell["filled_at"],
        "side" : filled_sell["side"],
        "profitability": profitability,
        "prediction": open_buy["prediction"]
        }
    
        db = getDb()
        
        db.child("sell").push(data)
        open_buy["open"] = 0
        db.child("buy").child(key).update(open_buy)
        print("BTC Sold")
        return Response("BTC Sold ", status=status.HTTP_200_OK)
    
    except requests.exceptions.RequestException as e:
        print("Sell Error:", e)

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
    
def getLastBuy():
    
    db = getDb()
    buy_ref = db.child("buy")
    
    data = buy_ref.get().val()
    
    if data:  
        keys = list(data.keys())
        
        last_key = keys[-1]
        
        last_entry = data[last_key]
        
        return last_entry, last_key
    
    return None

def getFilledTrade(id):
    getOrderByIdUrl = os.environ.get("GET_ORDER_BY_ID")
    r = requests.get(
    getOrderByIdUrl + id,
    headers={"APCA-API-KEY-ID": apiKey, "APCA-API-SECRET-KEY": secretKey},
    ).json()
    
    if r:
        return r
    else:
        return Exception("Order was not found, check that it was filled on Alpaca, otherwise it may be a timing issue")