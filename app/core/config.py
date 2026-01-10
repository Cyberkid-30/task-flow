from dotenv import load_dotenv
import os

load_dotenv()


class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "7NzFa4Nw1cDjRKyPSG8Fr+LpvIbhGRrXadktD9VVNKs=")
    DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///default.db")
    TOKEN_EXPIRE_MINUTES = int(os.getenv("TOKEN_EXPIRE_MINUTES", "15"))
