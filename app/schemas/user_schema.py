from pydantic import BaseModel, EmailStr


class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str


class UserLogin(BaseModel):
    username: str
    password: str


class UserResponse(BaseModel):
    id: str
    username: str
    email: EmailStr
    is_active: bool

    class Config:
        from_attributes = True


class ShowUser(BaseModel):
    username: str
    email: EmailStr

    class Config:
        from_attributes = True
