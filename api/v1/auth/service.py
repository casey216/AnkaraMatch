"""User service - Performs CRUD operations on users"""
from fastapi import HTTPException, status
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from api.v1.user.model import User
from api.v1.user.service import get_user_by_email
from api.v1.core.logger import logger

from .utils import verify_password, create_access_token, create_refresh_token, decode_access_token


def authenticate_user(email: str, password: str, db: Session) -> User | None:
    logger.info(f"Login attempt by {email}")
    db_user = get_user_by_email(db, email)
    if not db_user or not verify_password(password, db_user.hashed_password):
        logger.warning(f"Login attempt by {email} failed. Invalid credentials.")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password."
        )
    data = {
        "email": email
    }
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
    logger.info(f"User {email} logged in successfully.")
    
    return response

def refresh_access_token(db: Session, refresh_token: str):
    """Refreshes an expired JWT Token"""
    payload, error = decode_access_token(refresh_token)
    if error:
        logger.warning(f"Failed to refresh access token.\nError: {error}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={error}
        )
    
    user = get_user_by_email(db, payload.get("email"))
    if not user:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User not found"
        )
    data = {
        "email": user.email
    }
    new_access_token = create_access_token(data)
    
    return JSONResponse(content={
        "access_token": new_access_token,
        "token_type": "bearer"
    })
