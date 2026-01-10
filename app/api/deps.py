from typing import Annotated
from fastapi import Depends
from sqlalchemy.orm import Session
from core.database import get_db
from schemas.user_schema import UserResponse
from core.security import get_current_user

DBSession = Annotated[Session, Depends(get_db)]
Current_User_Dependency = Annotated[UserResponse, Depends(get_current_user)]
