from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    SECRET_KEY: str = "your_default_secret_key_here"
    DATABASE_URL: str = "sqlite+aiosqlite:///./test.db"
    SYNC_DATABASE_URL: str = "sqlite:///./test.db"
    TOKEN_EXPIRE_MINUTES: int = 15
    ENVIRONMENT: str = "DEVELOPMENT"

    def validate_config(self):
        """Validate that required environment variables are set"""
        if not self.SECRET_KEY:
            raise ValueError("SECRET_KEY environment variable is not set")
        if not self.DATABASE_URL:
            raise ValueError("DATABASE_URL environment variable is not set")
        if len(self.SECRET_KEY) < 32:
            raise ValueError("SECRET_KEY must be at least 32 characters long")
        if not self.DATABASE_URL.startswith("postgresql+asyncpg://"):
            raise ValueError(
                "DATABASE_URL must be a valid PostgreSQL connection string"
            )

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True


settings = Settings()
