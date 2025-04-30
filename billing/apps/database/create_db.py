import os
from datetime import datetime
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Boolean
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import declarative_base


def create_database(path):
    # engine = create_engine('sqlite:///mydatabase.db')
    file_path = os.path.join('sqlite:///', path)
    engine = create_engine(file_path)
    
    Session = sessionmaker(bind=engine)
    session = Session()
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
        task_id = Column(String)
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

    Base.metadata.create_all(engine)

    model = Models(name='Logistic Regression', cost = 10, description = "Логистическая регрессия — это статистическая модель, используемая для задач бинарной классификации (реже многоклассовой). В отличие от линейной регрессии, которая предсказывает непрерывные значения, логистическая регрессия предсказывает вероятность принадлежности объекта к определённому классу с помощью логистической функции (сигмоиды)")
    session.add(model)

    model = Models(name='Random Forest', cost = 50, description = "Случайный лес — это ансамблевая модель, основанная на множестве решающих деревьев (Decision Trees). Каждое дерево обучается на случайной подвыборке данных и признаков, а итоговый прогноз формируется путём усреднения (для регрессии) или голосования (для классификации) результатов всех деревьев.")
    session.add(model)

    model = Models(name='CatBoost', cost = 100, description = "CatBoost — это gradient boosting алгоритм, разработанный специально для работы с категориальными признаками. Он автоматически обрабатывает категориальные данные, преобразуя их в числовые, и использует упорядоченное boosting для борьбы с переобучением.")
    session.add(model)
    session.commit()

#users = session.query(User).filter(User.username=='admin').one()
#print(users.id, users.username, users.password)
#for user in users:
#     print(user.id, user.username, user.password)
