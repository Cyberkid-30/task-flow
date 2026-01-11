from datetime import date
from pydantic import BaseModel, field_validator, model_validator
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

    @model_validator(mode="after")
    def check_due_date_not_past(self):
        if self.due_date is not None and self.due_date < date.today():
            raise ValueError("due_date must be today or a future date")
        return self


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

    @model_validator(mode="after")
    def check_due_date_not_past(self):
        if self.due_date is not None and self.due_date < date.today():
            raise ValueError("due_date must be today or a future date")
        return self


class TaskResponse(BaseModel):
    id: str
    title: str
    description: str | None = None
    status: TaskStatus
    due_date: date | None = None
    owner: ShowUser

    class Config:
        from_attributes = True
