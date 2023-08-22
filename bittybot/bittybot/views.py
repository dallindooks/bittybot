import asyncio
import threading
from django.shortcuts import render
from requests import Request, Session
from requests.exceptions import ConnectionError, Timeout, TooManyRedirects
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view, renderer_classes
from rest_framework.renderers import JSONRenderer, TemplateHTMLRenderer
from django.http import HttpResponse, JsonResponse
import schedule
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
        return Response("Bot Started", status=status.HTTP_202_ACCEPTED)