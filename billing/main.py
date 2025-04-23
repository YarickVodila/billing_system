from apps.configs.config import Config
from apps.configs.base_schema import UserCreate, UserJWT, DataForPredict
from apps.database.db_helper import session
from apps.database.db_schema import User, UserTransaction, UserPrediction, Models

import os
from typing import Literal

import datetime

from fastapi import FastAPI, Depends, HTTPException
from fastapi.security import  HTTPBearer
from fastapi import FastAPI, HTTPException

from jose import jwt, JWTError

from passlib.context import CryptContext
from jose import JWTError, jwt, ExpiredSignatureError
import uvicorn

import bcrypt
import pandas as pd


bcrypt.__about__ = bcrypt
app = FastAPI()


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Защита маршрутов с использованием HTTPBearer
bearer = HTTPBearer()


def create_token(username: str):
    user = UserJWT(username=username)
    token_payload = user.model_dump(exclude_unset=True)
    
    # Время истечения токена
    token_payload.update({"exp": datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(minutes=Config.ACCESS_TOKEN_EXPIRE_MINUTES)})

    token = jwt.encode(token_payload, Config.SECRET_KEY)
    return token


@app.post("/login")
def login(user: UserJWT):
    
    db_user = session.query(User).filter(User.username == user.username).first()

    if db_user == None:
        raise HTTPException(status_code=401, detail="Пользователя нет. Зарегистрируйся")
    
    # if not pwd_context.verify(user.password, db_user.password):
    #     raise HTTPException(status_code=401, detail="Пароль неверный")
    
    db_user.authtime = datetime.datetime.now()
    session.commit()

    token = create_token(user.username)
    return {"access_token": token}


# =================================================================================================================================
# Защищаемые роуты, требующие авторизации.

def get_current_user(token: str = Depends(bearer)):
    try:
        # Проверяем JWT токен
        payload = jwt.decode(token.credentials, Config.SECRET_KEY)
        username = payload.get("username")
        # password = payload.get("password")

        # print(f"username: {username}")

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
def model_predict(model_id: Literal["1", "2", "3"], data: DataForPredict, user: str = Depends(get_current_user)):
    
    db_user = session.query(User).filter(User.username == user["username"]).first()

    # Получаем данный от пользователя
    data_x = pd.DataFrame({k:[v] for k, v in dict(data).items()})

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

    # ============================ Получаем прогноз =======================================

    predict = 0.5

    user_predict =  UserPrediction(
        user_id = db_user.id,
        timestamp = time_now,
        model_id = model_object.id,

        result = predict, # Результат прогноза
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


    return {"message": f"User: created successfully"}

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
        authtime=datetime.datetime.now(),
        balance=user_field.balance
    )

    session.add(db_user)
    session.commit()

    return {"message": f"User: `{user_field.username}` created successfully"}


if __name__ == "__main__":
    uvicorn.run("main:app", host='0.0.0.0', port=8000, log_level='info', reload=True)
