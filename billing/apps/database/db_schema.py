from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean

Base = declarative_base()

class User(Base):
    __tablename__ = 'Users'
    id = Column(Integer, primary_key=True, autoincrement = True)
    username = Column(String)
    email = Column(String)
    password = Column(String)
    authtime = Column(DateTime) 
    balance = Column(Float, default=5000)


class UserTransaction(Base):
    __tablename__ = 'UserTransaction'
    id = Column(Integer, primary_key=True, autoincrement = True)
    user_id = Column(Integer)
    timestamp = Column(DateTime)
    amount = Column(Float) # Объём транзакции транзакции
    type = Column(String) # Тип транзакции 'пополнение' / 'покупка' прогноза
    balance = Column(Float) # Баланс после транзакции
    
    
class TaskStatus(Base):
    __tablename__ = 'TaskStatus'
    id = Column(Integer, primary_key=True, autoincrement = True)
    user_id = Column(Integer)
    task_id = Column(String)


class UserPrediction(Base):
    __tablename__ = 'UserPrediction'
    id = Column(Integer, primary_key=True, autoincrement = True)
    user_id = Column(Integer)
    task_id = Column(String)
    status = Column(Boolean)
    timestamp = Column(DateTime)
    model_id = Column(Integer)

    result = Column(Float) # Результат прогноза
    person_age = Column(Integer)
    person_income = Column(Integer)
    person_emp_length = Column(Float)
    loan_intent = Column(String)
    loan_grade = Column(String)
    loan_amnt = Column(Integer)
    loan_int_rate = Column(Float)
    loan_percent_income = Column(Float)
    cb_person_default_on_file = Column(String)
    cb_person_cred_hist_length = Column(Integer)


class Models(Base):
    __tablename__ = 'Models'
    id = Column(Integer, primary_key=True, autoincrement = True)
    name = Column(String)
    cost = Column(Float)
    description = Column(String)