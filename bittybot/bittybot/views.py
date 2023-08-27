from datetime import datetime, timezone
import threading
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .tasks import start, pause
from .trades import getLastBuy, sellBTC
from .firebase import getDb

class startBot(APIView):
    
    botThread = None

    def post(self, request, format=None):
        global botThread
        botThread = threading.Thread(target=start)
        botThread.start()
        return Response("Bot Started", status=status.HTTP_202_ACCEPTED)
    
class killBot(APIView):
    def post(self, request, format=None):
        
        db = getDb()
    
        buy_ref = db.child("trades").get().val()
        print(buy_ref)
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