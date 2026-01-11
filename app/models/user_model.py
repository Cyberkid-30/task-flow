from datetime import datetime
from uuid import uuid4

from core.database import Base
from sqlalchemy import Column, DateTime, String, BOOLEAN
from sqlalchemy.orm import relationship


class User(Base):
    __tablename__ = "users"

    id = Column(String(36), primary_key=True, index=True, default=lambda: str(uuid4()))
    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_active = Column(BOOLEAN, default=True)
    created_at = Column(DateTime, default=lambda: datetime.now())
    updated_at = Column(
        DateTime,
        default=lambda: datetime.now(),
        onupdate=lambda: datetime.now(),
    )

    # Relationship to tasks owned by this user
    tasks = relationship(
        "Task",
        back_populates="owner",
        cascade="all, delete-orphan",
    )
