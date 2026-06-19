from datetime import datetime, timedelta, timezone, date
from enum import Enum as PyEnum
from uuid import uuid4

from sqlalchemy import DateTime, Date, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..core.database import Base


class TaskStatus(PyEnum):
    todo = "todo"
    in_progress = "in_progress"
    done = "done"
    cancelled = "cancelled"


class Task(Base):
    __tablename__ = "tasks"

    id: Mapped[str] = mapped_column(
        String, primary_key=True, index=True, default=lambda: str(uuid4())
    )
    title: Mapped[str] = mapped_column(String, nullable=False, index=True)
    description: Mapped[str] = mapped_column(String, nullable=False)
    status: Mapped[TaskStatus] = mapped_column(default=TaskStatus.todo, nullable=False)
    due_date: Mapped[date] = mapped_column(
        Date,
        nullable=True,
        default=lambda: (datetime.now(timezone.utc) + timedelta(days=7)).date(),
    )
    owner_id: Mapped[str] = mapped_column(
        String, ForeignKey("users.id"), nullable=False, index=True
    )
    owner = relationship("User", back_populates="tasks")

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    def to_dict(self):
        """Convert the Task model instance to a dictionary."""
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "status": self.status.value,
            "due_date": self.due_date.isoformat() if self.due_date else None,
            "owner_id": str(self.owner_id),
            "owner": self.owner.to_dict() if self.owner else None,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }
