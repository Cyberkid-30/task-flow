from datetime import date
from pydantic import BaseModel, field_validator
from models.task_model import TaskStatus
from uuid import UUID


class TaskCreate(BaseModel):
    title: str
    description: str | None = None
    status: TaskStatus | None = TaskStatus.todo
    due_date: date | None = None

    @field_validator("due_date", pre=True)  # type: ignore
    def parse_due_date(cls, v):
        if v is None:
            return None
        if isinstance(v, date):
            return v
        if isinstance(v, str):
            try:
                return date.fromisoformat(v)
            except Exception:
                raise ValueError("due_date must be a valid ISO 8601 date: YYYY-MM-DD")
        raise ValueError("due_date must be a date or ISO-8601 string")


class TaskUpdate(BaseModel):
    title: str
    description: str | None = None
    status: TaskStatus | None = TaskStatus.todo
    due_date: date | None = None

    @field_validator("due_date", pre=True)  # type: ignore
    def parse_due_date(cls, v):
        if v is None:
            return None
        if isinstance(v, date):
            return v
        if isinstance(v, str):
            try:
                return date.fromisoformat(v)
            except Exception:
                raise ValueError("due_date must be a valid ISO 8601 date: YYYY-MM-DD")
        raise ValueError("due_date must be a date or ISO-8601 string")


class TaskResponse(BaseModel):
    id: UUID
    title: str
    description: str | None = None
    status: TaskStatus
    due_date: date | None = None
    owner_id: str
    created_at: date
    updated_at: date

    class Config:
        from_attributes = True
