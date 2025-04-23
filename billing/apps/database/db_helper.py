from ..configs.config import Config

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


engine = create_engine(Config.DATABASE_URL)
Session = sessionmaker(bind=engine)
session = Session()