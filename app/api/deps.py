from typing import Annotated

from fastapi import Depends

from ..core.database import AsyncSession, get_async_db
from ..core.security import get_current_user
from ..schemas.user_schema import UserResponse

DB_Session = Annotated[AsyncSession, Depends(get_async_db)]
Current_User_Dependency = Annotated[UserResponse, Depends(get_current_user)]
