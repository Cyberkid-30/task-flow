from pydantic import BaseModel, EmailStr
from datetime import date


class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    id: str
    username: str
    email: EmailStr
    is_active: bool
    created_at: date
    updated_at: date

    class Config:
        from_attributes = True


class ShowUser(BaseModel):
    username: str
    email: EmailStr

    class Config:
        from_attributes = True
