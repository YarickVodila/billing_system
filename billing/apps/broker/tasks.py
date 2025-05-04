import os
import time
from joblib import dump, load

from celery import Celery
import numpy as np
import pandas as pd
from catboost import CatBoostClassifier, Pool

from dotenv import load_dotenv
load_dotenv()


CATEGORICAL_FEATURES = ["loan_intent", "loan_grade", "cb_person_default_on_file"]


# print(f"Текущая директория: {os.getcwd()}")

lr_model = load('apps/ml/models/linear_regression.joblib') 
rf_model = load('apps/ml/models/random_forest.joblib') 
encoder = load('apps/ml/models/encoder.joblib') 
scaler = load('apps/ml/models/scaler.joblib') 

catboost = CatBoostClassifier()
catboost.load_model("apps/ml/models/catboost")


# Инициализация Celery с Redis в качестве брокера
app_celery = Celery(
    'tasks',
    broker = os.getenv("BROKER", "redis://redis:6379/0"),
    backend = os.getenv("BACKEND", "redis://redis:6379/1")
)

def preprocessing(data):
    # data = data.drop(columns=["person_home_ownership"])

    categorical = encoder.transform(data[CATEGORICAL_FEATURES]).toarray()
    quantitative = scaler.transform(data.drop(columns = CATEGORICAL_FEATURES))
    return np.concatenate([categorical, quantitative], axis=1)

@app_celery.task
def lr_predict(data):
    data = pd.DataFrame(data)
    data = preprocessing(data)
    prob = lr_model.predict_proba(data)[:, 1][0]
    return prob


@app_celery.task
def rf_predict(data):
    data = pd.DataFrame(data)
    data = preprocessing(data)
    prob = rf_model.predict_proba(data)[:, 1][0]
    return prob

@app_celery.task
def catboost_predict(data):
    data = pd.DataFrame(data)
    prob = catboost.predict_proba(data)[:, 1][0]
    return prob