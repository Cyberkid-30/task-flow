from fastapi import APIRouter, HTTPException, status

from ...core.security import JWTHandler, Token, authenticate_user
from ...schemas.user_schema import UserCreate, UserLogin, UserResponse
from ...services.user_service import add_user
from ..deps import Current_User_Dependency, DB_Session

auth_router = APIRouter(prefix="/api/auth", tags=["Auth"])


@auth_router.post("/register", response_model=UserResponse)
async def create_user(db: DB_Session, request_body: UserCreate):
    new_user = await add_user(request_body, db)
    return new_user.to_dict()


@auth_router.post("/login", response_model=Token)
async def login(db: DB_Session, request_body: UserLogin):
    user = await authenticate_user(request_body.email, request_body.password, db)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid credentials"
        )

    token = JWTHandler.encode_data({"sub": user.username, "user_id": str(user.id)})
    return Token(access_token=token)


@auth_router.get("/me", response_model=UserResponse)
async def get_me(current_user: Current_User_Dependency):
    return current_user
