from .trades import evaluatePrediction
from .predictions import makePrediction
import asyncio
from apscheduler.schedulers.blocking import BlockingScheduler

scheduler = BlockingScheduler()

def predictAndTrade():
    evaluatePrediction(makePrediction())


def start():
    global scheduler
    job = scheduler.get_job("predictAndTrade")
    if job:
        scheduler.resume()
    else:
        scheduler.add_job(predictAndTrade, 'interval', minutes=1, id='predictAndTrade')
        scheduler.start()
    
def pause():
    global scheduler
    job = scheduler.get_job("predictAndTrade")
    if job:
        scheduler.pause()