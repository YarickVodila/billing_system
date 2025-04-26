import os
from celery import Celery
from dotenv import load_dotenv
import numpy as np
import time

# Инициализация Celery с Redis в качестве брокера
app_celery = Celery(
    'tasks',
    broker = os.getenv("BROKER", "redis://redis:6379/0"),
    backend = os.getenv("BACKEND", "redis://redis:6379/1")
)

@app_celery.task
def lr_predict(data):
    print(data)
    return np.random.random()

@app_celery.task
def rf_predict(data):
    print(data)
    return np.random.random()

@app_celery.task
def catboost_predict(data):
    print(data)
    return np.random.random()