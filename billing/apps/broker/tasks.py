import os
from celery import Celery
from dotenv import load_dotenv

import time

# Инициализация Celery с Redis в качестве брокера
app = Celery(
    'tasks',
    broker = os.getenv('BROKER'),
    backend = os.getenv('BACKEND')
)

@app.task
def lr_predict(data):

    return 0

@app.task
def rf_predict(data):
    
    return 0

@app.task
def catboost_predict(data):
    
    return 0