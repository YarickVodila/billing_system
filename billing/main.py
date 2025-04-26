from apps.configs.config import Config
from apps.configs.base_schema import UserCreate, UserJWT, DataForPredict, UserLogin
from apps.database.db_helper import session
from apps.database.db_schema import User, UserTransaction, UserPrediction, Models, TaskStatus
from apps.broker.tasks import lr_predict, rf_predict, catboost_predict, app_celery
from apps.database.create_db import create_database

from celery.result import AsyncResult

import os
from typing import Literal

import datetime

from fastapi import FastAPI, Depends, HTTPException, BackgroundTasks
from fastapi.security import  HTTPBearer
from fastapi import FastAPI, HTTPException

from jose import jwt, JWTError, ExpiredSignatureError

from passlib.context import CryptContext
import uvicorn

import bcrypt
import pandas as pd

import asyncio
from contextlib import asynccontextmanager

bcrypt.__about__ = bcrypt


async def monitor_task():
    """Фоновая задача для периодического мониторинга таблицы."""
    while True:
        try:
            all_tasks = session.query(TaskStatus).all()

            for task in all_tasks:
                result_task = AsyncResult(task.task_id, app=app_celery)

                if result_task.ready(): # Если таска выполнена
                    db_prediction = session.query(UserPrediction).filter( # Обновляем прогноз пользователя
                        UserPrediction.user_id == task.user_id,
                        UserPrediction.task_id == task.task_id,
                    ).first()

                    db_prediction.result = result_task.get() 
                    db_prediction.status = True 
                    session.delete(task) # Удаляем таску из таблицы
            
            session.commit()
            
        except Exception as e:
            print(f"Error monitoring table: {e}")
        
        await asyncio.sleep(10)  # Ждем 10 секунд


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Контекстный менеджер для управления жизненным циклом приложения"""

    # Код до yield выполняется при старте приложения

    
    # file_path = os.path.join('db', 'mydatabase.db')
    # print(f"Проверка нахождения базы по пути: {file_path} - {os.path.exists(file_path)}")
    # # Проверка существования файла
    # if os.path.exists(file_path):
    #     print("Создаём базу данных")
    #     create_database(file_path)


    monitor = asyncio.create_task(monitor_task())

    yield  # Здесь приложение работает
    
    # Код после yield выполняется при остановке приложения
    monitor.cancel()
    try:
        await monitor_task
    except asyncio.CancelledError:
        pass
    print("Monitoring task stopped gracefully")


app = FastAPI(lifespan=lifespan)




pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Защита маршрутов с использованием HTTPBearer
bearer = HTTPBearer()


def create_token(username: str):
    user = UserJWT(username = username)
    token_payload = user.model_dump(exclude_unset=True)
    
    # Время истечения токена
    token_payload.update({"exp": datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(minutes=Config.ACCESS_TOKEN_EXPIRE_MINUTES)})

    token = jwt.encode(token_payload, Config.SECRET_KEY)
    return token


@app.post("/login")
def login(user: UserLogin):
    
    username = user.username
    password = user.password

    db_user = session.query(User).filter(
        User.username == username,
        # User.password == password
    ).first()

    if db_user == None:
        raise HTTPException(status_code=401, detail="Пользователя нет. Зарегистрируйся")
    
    if not pwd_context.verify(password, db_user.password):
        raise HTTPException(status_code=401, detail="Пароль неверный")
    
    db_user.authtime = datetime.datetime.now()
    session.commit()

    token = create_token(username)
    return {"access_token": token}


# =================================================================================================================================
# Защищаемые роуты, требующие авторизации.

def get_current_user(token: str = Depends(bearer)):
    try:
        # Проверяем JWT токен
        payload = jwt.decode(token.credentials, Config.SECRET_KEY)
        username = payload.get("username")

        # Получаем пользователя из БД
        db_user = session.query(User).filter(User.username == username).first()
        if db_user == None:
            raise HTTPException(status_code=401, detail="Пользователя нет. Зарегистрируйся")

        # if not pwd_context.verify(password, db_user.password):
        #     raise HTTPException(status_code=401, detail="Пароль неверный")
        
        user = {
            "id": db_user.id,
            "username": db_user.username,
            "balance": db_user.balance,
        }

        return user
    
    except ExpiredSignatureError:
        raise HTTPException(status_code=403, detail="Время жизни токена истекло")
    
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")





@app.post("/predict")
def model_predict(model_id: Literal["1", "2", "3"], data: DataForPredict, user: dict = Depends(get_current_user)):
    
    db_user = session.query(User).filter(User.username == user["username"]).first()
    
    print(f'Data: {dict(data).items()}')

    # Получаем данный от пользователя
    # data_x = pd.DataFrame({k:[v] for k, v in dict(data).items()})
    data_x = {k:[v] for k, v in dict(data).items()}

    # Получаем информацию о модели которую хотим использовать
    model_object = session.query(Models).filter(Models.id==int(model_id)).first()
    
    update_balance = db_user.balance - model_object.cost

    if update_balance < 0:
        raise HTTPException(status_code=422, detail="Недостаточно денег на балансе")

    # Обновляем баланс пользователя
    db_user.balance = update_balance

    time_now = datetime.datetime.now()

    user_transaction = UserTransaction(
        user_id = db_user.id,
        timestamp = time_now,
        amount = model_object.cost, # Объём транзакции транзакции
        type = "покупка", # Тип транзакции 'пополнение' / 'покупка' прогноза
        balance = db_user.balance, # Баланс после транзакции
    )

    session.add(user_transaction)

    if model_object.id == 1:
        id_task = lr_predict.delay(data_x)

    elif model_object.id == 2:
        id_task = rf_predict.delay(data_x)

    else:
        id_task = catboost_predict.delay(data_x)
    
    task_status = TaskStatus(
        user_id = db_user.id,
        task_id = id_task.id
    )

    session.add(task_status)

    # ============================ Создаём прогноз =======================================

    user_predict = UserPrediction(
        user_id = db_user.id,
        timestamp = time_now,
        model_id = model_object.id,
        task_id = id_task.id, # id задачи
        status = False, # Задача в очереди

        result = 0, # Результат прогноза
        person_age = data.person_age,
        person_income = data.person_income,
        person_emp_length = data.person_emp_length,
        loan_intent = data.loan_intent,
        loan_grade = data.loan_grade,
        loan_amnt = data.loan_amnt,
        loan_int_rate = data.loan_int_rate,
        loan_percent_income = data.loan_percent_income,
        cb_person_default_on_file = data.cb_person_default_on_file,
        cb_person_cred_hist_length = data.cb_person_cred_hist_length,
    )
    
    session.add(user_predict)

    # =====================================================================================
    
    session.commit()


    return {"message": f"Task in processing", "task_id": id_task.id}



@app.post("/balance_replenish")
def balance_replenish(amount:int, user: dict = Depends(get_current_user)):
    
    db_user = session.query(User).filter(User.username == user["username"]).first()
    db_user.balance = db_user.balance + amount
    
    time_now = datetime.datetime.now()

    user_transaction = UserTransaction(
        user_id = db_user.id,
        timestamp = time_now,
        amount = amount, # Объём транзакции транзакции
        type = "пополнение", # Тип транзакции 'пополнение' / 'покупка' прогноза
        balance = db_user.balance, # Баланс после транзакции
    )

    session.add(user_transaction)
    session.commit()

    return {"message": f"Баланс пополнен на {amount} бумажек с мёртвыми президентами"}

@app.get("/get_model_desc")
def get_model_desc():
    
    models = session.query(Models).all()

    data = [
        {column.name: getattr(item, column.name) for column in item.__table__.columns} for item in models
    ]

    return {"data": data}

@app.get("/get_statistic")
def get_statistic(user: dict = Depends(get_current_user)):
    
    user = session.query(User).filter(User.username == user["username"]).first()

    user_statistic = session.query(UserPrediction).filter(
        UserPrediction.user_id == user.id,
        UserPrediction.status == True
    ).all()

    data = [
        {column.name: getattr(item, column.name) for column in item.__table__.columns if column.name not in ["id", "status", "user_id", "task_id"]} for item in user_statistic
    ]

    return {"data": data}

@app.get("/get_history_transaction")
def get_history_transaction(type_trans: Literal["пополнение", "покупка"], user: dict = Depends(get_current_user)):
    
    user = session.query(User).filter(User.username == user["username"]).first()

    user_statistic = session.query(UserTransaction).filter(
        UserTransaction.user_id == user.id,
        UserTransaction.type == type_trans
    ).all()

    data = [
        {column.name: getattr(item, column.name) for column in item.__table__.columns if column.name not in ["id", "user_id"]} for item in user_statistic
    ]

    return {"data": data}

@app.get("/user")
def get_user(user: dict = Depends(get_current_user)):
    return user



# =================================================================================================================================


@app.post("/register")
async def register_user(user_field: UserCreate):
    user = session.query(User).filter(User.username==user_field.username).first()

    if user != None:
        raise HTTPException(status_code=400, detail="Username already registered")
    
    hashed_password = pwd_context.hash(user_field.password)

    db_user = User(
        username=user_field.username,
        email=user_field.email,
        password=hashed_password,
        authtime=datetime.datetime.now()
        # balance=user_field.balance
    )

    session.add(db_user)
    session.commit()

    return {"message": f"User: `{user_field.username}` created successfully"}



if __name__ == "__main__":
    uvicorn.run("main:app", host='0.0.0.0', port=8000, log_level='info', reload=True)
