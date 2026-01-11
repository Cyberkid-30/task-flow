from fastapi import APIRouter, HTTPException, status
from schemas.user_schema import UserCreate, UserLogin, UserResponse
from ..deps import DBSession, Current_User_Dependency
from models.user_model import User
from sqlalchemy import or_, func
from core.security import Bcrypt, Token, authenticate_user, JWTHandler


auth_router = APIRouter(prefix="/api/auth", tags=["Auth"])


@auth_router.post("/register", response_model=UserResponse)
def create_user(db: DBSession, request: UserCreate):
    # normalize inputs
    normalized_username = request.username.strip()
    normalized_email = request.email.strip().lower()

    # check if a user with same username OR email exists (email check is case-insensitive)
    existing_user = (
        db.query(User)
        .filter(
            or_(
                User.username == normalized_username,
                func.lower(User.email) == normalized_email,
            )
        )
        .first()
    )

    if existing_user:
        if existing_user.username == normalized_username:  # type: ignore
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="A user with this username already exists",
            )
        if existing_user.email and existing_user.email.lower() == normalized_email:  # type: ignore
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="A user with this email already exists",
            )

    new_user = User(
        username=normalized_username,
        email=normalized_email,
        hashed_password=Bcrypt.hash_password(request.password),
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


@auth_router.post("/login", response_model=Token)
def login(db: DBSession, request: UserLogin):
    user = authenticate_user(request.email, request.password, db)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid credentials"
        )

    token = JWTHandler.encode_data({"sub": user.username, "user_id": user.id})
    return Token(access_token=token)


@auth_router.get("/me", response_model=UserResponse)
def get_me(user: Current_User_Dependency):
    return user
