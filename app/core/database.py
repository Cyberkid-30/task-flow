from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool, QueuePool
import os

from .config import Config

# Use NullPool for better compatibility with serverless/Render environments
# Use QueuePool for local development
pool_class = NullPool if os.getenv("RENDER") == "true" else QueuePool

# Configure engine with retry logic for better Render compatibility
engine_config = {
    "url": Config.DATABASE_URL,  # type: ignore
    "poolclass": pool_class,
    "pool_pre_ping": True,  # Verify connections before using them
    "echo": False,
    "connect_args": {"connect_timeout": 30, "application_name": "task-flow-api"},
}

# Add connection pooling settings for production
if not os.getenv("RENDER") == "true":
    engine_config.update(
        {
            "pool_size": 5,
            "max_overflow": 10,
            "pool_timeout": 30,
            "pool_recycle": 3600,
        }
    )

engine = create_engine(**engine_config)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
