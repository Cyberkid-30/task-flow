from datetime import datetime, timedelta

from core.database import get_db
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from models.user_model import User
from pwdlib import PasswordHash
from pwdlib.hashers.bcrypt import BcryptHasher
from pydantic import BaseModel
from schemas.user_schema import UserResponse
from sqlalchemy.orm import Session

from .config import Config

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")


pwd_context = PasswordHash([BcryptHasher()])
ALGORITHM = "HS256"


class Bcrypt:
    @staticmethod
    def hash_password(password: str) -> str:
        return pwd_context.hash(password)

    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        return pwd_context.verify(plain_password, hashed_password)


class Token(BaseModel):
    access_token: str
    token_type: str = "Bearer"


class JWTHandler:
    @staticmethod
    def encode_data(
        data: dict,
        secret_key: str = Config.SECRET_KEY,  # type: ignore
        algorithm: str = ALGORITHM,
        expires_in: timedelta | None = None,
    ) -> str:
        to_encode = data.copy()
        if expires_in:
            expires = expires_in
        else:
            expires = datetime.now() + timedelta(minutes=Config.TOKEN_EXPIRE_MINUTES)
        to_encode.update({"exp": expires})

        return jwt.encode(to_encode, secret_key, algorithm=algorithm)

    @staticmethod
    def decode_token(
        token: str,
        secret_key: str = Config.SECRET_KEY,  # type: ignore
        algorithms: list[str] = [ALGORITHM],
    ) -> dict:
        try:
            payload = jwt.decode(token, secret_key, algorithms=algorithms)
            return payload
        except JWTError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token. Could not validate user",
            )


def authenticate_user(username: str, password: str, db: Session):
    user = db.query(User).filter(User.username == username).first()
    if not user:
        return False

    if not Bcrypt.verify_password(password, user.hashed_password):  # type: ignore
        return False

    return user


def validate_token(token: str) -> dict:
    """Decode and validate the JWT token."""
    payload = JWTHandler.decode_token(token)
    username = payload.get("sub")
    user_id = payload.get("user_id")

    if not username or not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token. Could not validate user",
        )

    return payload


def get_user_by_id(db: Session, user_id: str) -> User:
    """Fetch a user by their ID."""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )
    return user


def get_current_user(
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme),
) -> UserResponse:
    """Retrieve the current user based on the provided JWT token."""
    payload = validate_token(token)
    user = get_user_by_id(db, payload["user_id"])
    return UserResponse(**user.__dict__)
