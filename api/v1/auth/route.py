from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordRequestForm
from typing import Annotated
from sqlalchemy.orm import Session

from api.v1.core.database import get_db
from .schema import Token, UserRegistration, UserResponse
from .service import create_user, authenticate_user
from .utils import create_access_token, create_refresh_token, decode_access_token
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
        logger.warning(f"Login attempt by {form_data.username} failed. Invalid credentials.")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password."
        )
    data = {
        "email": user.email
    }
    logger.info(f"User {form_data.username} logged in successfully.")
    access_token = create_access_token(data)
    refresh_token = create_refresh_token(data)

    response = JSONResponse(content={
        "access_token": access_token,
        "token_type": "bearer"
    })

    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        samesite="strict",
        secure=True,
        max_age=7 * 24 * 60 * 60
    )

    return response

@auth.post("refresh_token", response_model=Token)
def refresh_token(request: Request):
    refresh_token = request.cookies.get("refresh_token")
    if not refresh_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh Token not found"
        )
    
    payload = decode_access_token(refresh_token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token"
        )
    
    data = {
        "email": payload["email"]
    }
    new_access_token = create_access_token(data)

    return JSONResponse(content={
        "access_token": new_access_token,
        "token_type": "bearer"
    })