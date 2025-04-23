import os
from celery import Celery
from dotenv import load_dotenv
from ..configs.config import Config
import numpy as np
import time

# Инициализация Celery с Redis в качестве брокера
app_celery = Celery(
    'tasks',
    broker = Config.BROKER,
    backend = Config.BACKEND
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