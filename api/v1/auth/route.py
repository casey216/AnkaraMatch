from fastapi import APIRouter, Depends
from typing import Annotated
from sqlalchemy.orm import Session

from api.v1.core.database import get_db
from .schema import UserLogin, UserRegistration, UserResponse
from .service import create_user

auth = APIRouter(prefix="/auth", tags=["Auth"])

@auth.post("/register", response_model=UserResponse)
def register(user: UserRegistration, db: Annotated[Session, Depends(get_db)]):
    return create_user(user, db)
