from ..configs.config import Config
from apps.database.create_db import create_database
import os
from sqlalchemy import create_engine, inspect
from sqlalchemy.orm import sessionmaker


file_path = os.path.join('db', 'mydatabase.db')


engine = create_engine(os.path.join('sqlite:///', Config.DATABASE_URL))
inspector = inspect(engine)
# Получаем список всех таблиц
tables = inspector.get_table_names()
if not tables:
    print("База данных пустая (нет таблиц). Создаём базу данных")
    create_database(file_path)
else:
    print(f"В базе есть таблицы: {tables}")

Session = sessionmaker(bind=engine)
session = Session()