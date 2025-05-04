from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean

Base = declarative_base()

class User(Base):
    __tablename__ = 'Users'
    id = Column(Integer, primary_key=True, autoincrement = True)
    username = Column(String) # Имя пользователя
    email = Column(String) # Имейл пользователя
    password = Column(String) # Пароль пользователя
    authtime = Column(DateTime) # Время последней авторизации
    balance = Column(Float, default=5000) # 


class UserTransaction(Base):
    __tablename__ = 'UserTransaction'
    id = Column(Integer, primary_key=True, autoincrement = True)
    user_id = Column(Integer) # id пользователя
    task_id = Column(String) # id задачи
    timestamp = Column(DateTime) # Время транзакции
    amount = Column(Float) # Объём транзакции транзакции
    type = Column(String) # Тип транзакции 'пополнение' / 'покупка' прогноза
    balance = Column(Float) # Баланс после транзакции
    
    
class TaskStatus(Base):
    __tablename__ = 'TaskStatus'
    id = Column(Integer, primary_key=True, autoincrement = True)
    user_id = Column(Integer) # id пользователя
    task_id = Column(String) # id задачи


class UserPrediction(Base):
    __tablename__ = 'UserPrediction'
    id = Column(Integer, primary_key=True, autoincrement = True)
    user_id = Column(Integer) # id пользователя
    task_id = Column(String) # id задачи
    status = Column(Boolean) # Статус выполнения задачи
    timestamp = Column(DateTime) # Время выполнения создания \ выполнения прогноза
    model_id = Column(Integer) # id модели, которую использовали для прогноза

    result = Column(Float) # Результат прогноза
    person_age = Column(Integer) # возраст кандидата.
    person_income = Column(Integer) # сколько денег кандидат зарабатывает в год.
    person_emp_length = Column(Float) # сколько лет работает кандидат.
    loan_intent = Column(String) # причина, по которой кандидату нужен кредит.
    loan_grade = Column(String) # оценка, показывающая, насколько кандидат надежен в погашении кредитов.
    loan_amnt = Column(Integer) #  сумма денег, которую кандидат хочет занять.
    loan_int_rate = Column(Float)  # процентная ставка, взимаемая по кредиту.
    loan_percent_income = Column(Float) # какой процент дохода кандидата пойдет на выплаты по кредиту.
    cb_person_default_on_file = Column(String) # показывает, были ли просрочки по кредиту у кандидата.
    cb_person_cred_hist_length = Column(Integer) # Как долго у кандидата была кредитная история 


class Models(Base):
    __tablename__ = 'Models'
    id = Column(Integer, primary_key=True, autoincrement = True)
    name = Column(String) # Название модели
    cost = Column(Float) # Цена прогноза модели
    description = Column(String) # Описание модели