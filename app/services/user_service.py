from fastapi import HTTPException, status
from ..schemas.user_schema import UserCreate
from ..models.user_model import User
from sqlalchemy import or_, func, select
from ..core.security import Bcrypt
from ..core.database import AsyncSession


async def add_user(user_data: UserCreate, db: AsyncSession):
    normalized_username = user_data.username.strip()
    normalized_email = user_data.email.strip().lower()

    # check if a user with same username OR email exists (email check is case-insensitive)
    result = await db.execute(
        select(User).where(
            or_(
                User.username == normalized_username,
                func.lower(User.email) == normalized_email,
            )
        )
    )
    existing_user = result.scalar_one_or_none()

    if existing_user:
        if str(existing_user.username) == normalized_username:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="A user with this username already exists",
            )
        if existing_user.email.lower() == normalized_email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="A user with this email already exists",
            )

    new_user = User(
        username=normalized_username,
        email=normalized_email,
        hashed_password=Bcrypt.hash_password(user_data.password),
    )
    db.add(new_user)

    try:
        await db.commit()
        await db.refresh(new_user)
    except Exception as e:
        await db.rollback()
        raise e

    return new_user


async def get_user_by_id(db: AsyncSession, user_id: str):
    """Fetch a user by their ID."""
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    return user
