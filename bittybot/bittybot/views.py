import threading
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .tasks import start, pause

class startBot(APIView):
    
    botThread = None

    def post(self, request, format=None):
        global botThread
        botThread = threading.Thread(target=start)
        botThread.start()
        return Response("Bot Started", status=status.HTTP_202_ACCEPTED)
    
class killBot(APIView):
    def post(self, request, format=None):
        pause()
        return Response("Bot Paused", status=status.HTTP_202_ACCEPTED)
    