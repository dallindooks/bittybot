from datetime import datetime, timedelta, timezone
import json
import pyrebase
import threading
from django.http import JsonResponse
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .tasks import start, pause
from .trades import getLastBuy, sellBTC
from .firebase import getDb
import atexit
from google.oauth2 import id_token
from google.auth.transport import requests
from firebase_admin import credentials, auth
import os
import firebase_admin
from firebase_admin import credentials

token = ''

def shutdown_function():
    print("Server is shutting down. Performing cleanup.")
    db = getDb()
        
    bot_run_ref = db.child("bot_running").update({"on": False})
    
    buy_ref = db.child("trades").get().val()
    
    global token
    token = ''

    pause()
    open_buy_tuple = getLastBuy()

    if open_buy_tuple:
        if open_buy_tuple[0]["open"] == 1:
            sellBTC(open_buy_tuple)

atexit.register(shutdown_function)

class startBot(APIView):
    
    botThread = None
    def post(self, request, format=None):
        global botThread
        
        token = request.data.get('token')
        db = getDb()
        if adminAuthVerify(token) == "authenticated":
        
            bot_run_ref = db.child("bot_running").update({"on": True})
            botThread = threading.Thread(target=start)
            botThread.start()
            return Response("Bot Started", status=status.HTTP_202_ACCEPTED)
        
        return Response("User not authenticated", status=status.HTTP_418_IM_A_TEAPOT)
    
class killBot(APIView):
    def post(self, request, format=None):
        
        db = getDb()
        
        bot_run_ref = db.child("bot_running").update({"on": False})
    
        buy_ref = db.child("trades").get().val()
        pause()
        open_buy_tuple = getLastBuy()
    
        if open_buy_tuple:
            if open_buy_tuple[0]["open"] == 1:
                sellBTC(open_buy_tuple)
                
        return Response("Bot Paused", status=status.HTTP_202_ACCEPTED)

class profitableCount(APIView):   
    def get(self, request, start, format=None):
 
        start_date = datetime.strptime(start, "%m-%d-%Y")
        
        db = getDb()
        sell_ref = db.child("sell").get()
        
        profitable = 0
        unprofitable = 0
                
        for sell_data in sell_ref.each():
            trade_date_str = sell_data.val().get("sell_time")
            trade_date = datetime.strptime(trade_date_str[:-4], "%Y-%m-%dT%H:%M:%S.%f")
            trade_profitability = float(sell_data.val().get("profitability"))
            
            if start_date < trade_date and trade_profitability > 0:
                profitable += 1
            elif start_date < trade_date and trade_profitability < 0:
                unprofitable += 1  
                
        return Response({"profitable_trades": profitable, "unprofitable_trades": unprofitable}, status=status.HTTP_200_OK)
    
class profitabilities(APIView):
    def get(self, request, start, format=None):
        start_date = datetime.strptime(start, "%m-%d-%Y")
        start_date = start_date - timedelta(days=7)
        
        profitabilities_arr = []
        
        db = getDb()
        sell_ref = db.child("sell").get()
        
        for sell_data in sell_ref.each():
            trade_date_str = sell_data.val().get("sell_time")
            trade_date = datetime.strptime(trade_date_str[:-4], "%Y-%m-%dT%H:%M:%S.%f")
            trade_profitability = float(sell_data.val().get("profitability"))
            
            if start_date < trade_date:
                profitabilities_arr.append({"trade_time": trade_date, "profit": trade_profitability})
                
        return Response(profitabilities_arr, status=status.HTTP_200_OK) 
    
class profitVsCertainty(APIView):
    def get(self, request, start, format=None):
        start_date = datetime.strptime(start, "%m-%d-%Y")
        
        profitabilities_arr = []
        
        db = getDb()
        sell_ref = db.child("sell").get()
        
        for sell_data in sell_ref.each():
            trade_date_str = sell_data.val().get("sell_time")
            trade_date = datetime.strptime(trade_date_str[:-4], "%Y-%m-%dT%H:%M:%S.%f")
            trade_profitability = float(sell_data.val().get("profitability"))
            buy_price = float(sell_data.val().get("buy_price"))
            certainty = float(sell_data.val().get("prediction"))
            percent_profitable = trade_profitability / buy_price
            
            if start_date < trade_date:
                profitabilities_arr.append({"profit_percent": percent_profitable, "certainty": certainty})
                
        return Response(profitabilities_arr, status=status.HTTP_200_OK)
    
    
class botRunning(APIView):
    def get(self, request, format=None):
        db = getDb()
        bot_ref = db.child("bot_running").child("on").get()
        return Response(bot_ref.val(), status=status.HTTP_200_OK)
    

def adminAuthVerify(token):

    id_token_str = token
    
    firebase = pyrebase.initialize_app(os.environ.get('FIREBASE_CONFIG'))
    auth = firebase.auth()
    
    decoded_token = auth.verify_id_token(id_token_str)
    user_email = decoded_token["email"]

    try:
        id_info = id_token.verify_oauth2_token(id_token_str, requests.Request(), "YOUR_GOOGLE_CLIENT_ID")
        if user_email:
            if user_email == os.environ.get("ADMIN_AUTH_USER"):
                return "authenticated"
    except ValueError as e:
        return JsonResponse({"error": "Invalid ID token"}, status=400)
    
class saveToken(APIView):
    def post(self, request, format=None):
        global token
        
        token = request.data.get('token')
        
        return Response("token saved thnks", status=status.HTTP_200_OK)