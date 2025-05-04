from apps.database.create_db import create_database
import os
import logging

from sqlalchemy import create_engine, inspect
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

file_path = os.path.join('db', 'mydatabase.db')


engine = create_engine(os.path.join('sqlite:///', os.getenv("DATABASE_URL")))
inspector = inspect(engine)
# Получаем список всех таблиц
tables = inspector.get_table_names()
if not tables:
    # print("База данных пустая (нет таблиц). Создаём базу данных")
    logger.info("База данных пустая (нет таблиц). Создаём базу данных")
    create_database(file_path)
else:
    # print(f"В базе есть таблицы: {tables}")
    logger.info(f"В базе есть таблицы: {tables}")

Session = sessionmaker(bind=engine)
session = Session()