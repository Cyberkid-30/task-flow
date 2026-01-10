from datetime import date, datetime
from pydantic import BaseModel, field_validator
from models.task_model import TaskStatus
from .user_schema import ShowUser


class TaskCreate(BaseModel):
    title: str
    description: str | None = None
    status: TaskStatus | None = TaskStatus.todo
    due_date: date | None = None

    @field_validator("due_date")  # type: ignore
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

    @field_validator("due_date")  # type: ignore
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
    id: str
    title: str
    description: str | None = None
    status: TaskStatus
    due_date: date | None = None
    owner: ShowUser

    class Config:
        from_attributes = True
