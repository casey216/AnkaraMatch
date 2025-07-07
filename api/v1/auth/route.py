from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from typing import Annotated
from sqlalchemy.orm import Session

from api.v1.core.database import get_db
from .schema import Token, UserRegistration, UserResponse
from .service import create_user, authenticate_user
from .utils import create_access_token
from .model import User
from ..core.logger import logger

auth = APIRouter(prefix="/auth", tags=["Auth"])

@auth.post("/register", response_model=UserResponse)
def register(user: UserRegistration, db: Annotated[Session, Depends(get_db)]):
    return create_user(user, db)


@auth.post("/login", response_model=Token)
def login(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: Annotated[Session, Depends(get_db)]
):
    logger.info(f"Login attempt by {form_data.username}")
    user: User = authenticate_user(form_data.username, form_data.password, db)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password."
        )
    data = {
        "email": user.email
    }
    logger.info(f"User {form_data.username} logged in successfully.")
    return create_access_token(data)

