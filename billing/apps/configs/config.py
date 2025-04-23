class Config:
    DATABASE_URL = 'sqlite:///../mydatabase.db'
    BROKER = 'redis://localhost:6379/0'
    BACKEND = 'redis://localhost:6379/1'
    SECRET_KEY = "Data_Secrets"
    ACCESS_TOKEN_EXPIRE_MINUTES = 60

