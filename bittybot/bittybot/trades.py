from rest_framework import status
from rest_framework.response import Response
import os
import dotenv
import requests


accountUrl = os.getenv('GET_ACCOUNT_URL')
tradeUrl = os.getenv('CREATE_ORDER_URL')
apiKey = os.getenv("API_KEY")
secretKey = os.getenv("SECRET_KEY")
dotenv.load_dotenv()

def evaluatePrediction(prediction):
    date = prediction.keys()
    
    predValue = prediction[0]
    
    if (predValue > .65):
        # buy here
        return
    elif (predValue < .35):
        # sell here
        return
    
def buyBTC():
    
    global tradeUrl
    try:
        cash = getCurrentCash()
        amount = cash * 0.05 
        print(amount)
        buyCall = requests.post(tradeUrl, headers={"APCA-API-KEY-ID": apiKey, "APCA-API-SECRET-KEY": secretKey},
                    params={"side": "buy", "type": "market", "time_in_force": "ioc", "symbol": "BTC/USD", "notional": str(amount)})
        return Response("BTC Bought", status=status.HTTP_200_OK)
    except:
        Exception("unable to retrieve cash")

def sellBTC():
    return

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

buyBTC()
# print(buyBTC())