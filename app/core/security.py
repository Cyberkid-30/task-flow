from datetime import datetime, timedelta

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from pwdlib import PasswordHash
from pwdlib.hashers.bcrypt import BcryptHasher
from pydantic import BaseModel
from sqlalchemy import select

from ..core.database import AsyncSession, get_async_db
from ..models.user_model import User
from ..schemas.user_schema import UserResponse
from .config import settings

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
        secret_key: str = settings.SECRET_KEY,  # type: ignore
        algorithm: str = ALGORITHM,
        expires_in: timedelta | None = None,
    ) -> str:
        to_encode = data.copy()
        if expires_in:
            expires = datetime.now() + expires_in
        else:
            expires = datetime.now() + timedelta(minutes=settings.TOKEN_EXPIRE_MINUTES)
        to_encode.update({"exp": expires})

        return jwt.encode(to_encode, secret_key, algorithm=algorithm)

    @staticmethod
    def decode_token(
        token: str,
        secret_key: str = settings.SECRET_KEY,  # type: ignore
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


async def authenticate_user(email: str, password: str, db: AsyncSession):
    result = await db.execute(select(User).where(User.email == email))
    user = result.scalar_one_or_none()

    if not user or not Bcrypt.verify_password(password, user.hashed_password):  # type: ignore
        return

    return user


async def get_current_user(
    db: AsyncSession = Depends(get_async_db),
    token: str = Depends(oauth2_scheme),
) -> UserResponse:
    """Retrieve the current user based on the provided JWT token."""
    payload = JWTHandler.decode_token(token)

    result = await db.execute(select(User).where(User.username == payload.get("sub")))
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authorized to access this resource",
        )

    return UserResponse(**user.to_dict())
