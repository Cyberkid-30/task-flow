from dotenv import load_dotenv
import os

load_dotenv()


class Config:
    SECRET_KEY = os.getenv("SECRET_KEY")
    DATABASE_URL = os.getenv("DATABASE_URL")
    TOKEN_EXPIRE_MINUTES = int(os.getenv("TOKEN_EXPIRE_MINUTES", "15"))
    ENVIRONMENT = os.getenv("ENVIRONMENT", "production")

    @classmethod
    def validate_config(cls):
        """Validate that required environment variables are set"""
        if not cls.SECRET_KEY:
            raise ValueError("SECRET_KEY environment variable is not set")
        if not cls.DATABASE_URL:
            raise ValueError("DATABASE_URL environment variable is not set")
        if len(cls.SECRET_KEY) < 32:
            raise ValueError("SECRET_KEY must be at least 32 characters long")
        if not cls.DATABASE_URL.startswith(("postgresql://", "postgres://")):
            raise ValueError(
                "DATABASE_URL must be a valid PostgreSQL connection string"
            )
