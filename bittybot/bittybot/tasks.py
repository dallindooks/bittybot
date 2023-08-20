import schedule
import time
import predictions
from apscheduler.schedulers.blocking import BlockingScheduler

def predictAndTrade():
    print(predictions.makePrediction())
    
# schedule.every(0.1).minutes.do(predictAndTrade)


def start():
    scheduler = BlockingScheduler()
    scheduler.add_job(predictAndTrade, 'interval', minutes=0.05, id='predictAndTrade')
    scheduler.start()
    
def pause():
    scheduler = BlockingScheduler()
    job = scheduler.get_job("predictAndTrade")
    if job:
        scheduler.pause()