from .predictions import makePrediction
import asyncio
from apscheduler.schedulers.blocking import BlockingScheduler

scheduler = BlockingScheduler()

def predictAndTrade():
    print(makePrediction())


def start():
    global scheduler
    scheduler.add_job(predictAndTrade, 'interval', minutes=0.05, id='predictAndTrade')
    scheduler.start()
    
def pause():
    global scheduler
    job = scheduler.get_job("predictAndTrade")
    if job:
        scheduler.pause()