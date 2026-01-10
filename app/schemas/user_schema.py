from pydantic import BaseModel, EmailStr
from uuid import UUID


class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str


class UserLogin(BaseModel):
    username: str
    password: str


class UserResponse(BaseModel):
    id: UUID
    username: str
    email: EmailStr
    is_active: bool

    class Config:
        from_attributes = True
