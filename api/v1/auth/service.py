"""User service - Performs CRUD operations on users"""
from fastapi import Depends, HTTPException, status
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from pydantic import EmailStr
from typing import Annotated

from .model import User
from .schema import UserRegistration
from ..core.database import get_db
from .utils import hash_password, verify_password, create_access_token, create_refresh_token, decode_access_token
from ..core.logger import logger


def create_user(user: UserRegistration, db: Annotated[Session, Depends(get_db)]):
    """Creates new user"""
    logger.info(f"Creating user: {user.email}")
    db_user = User(
        name=user.name,
        email=user.email,
        hashed_password=hash_password(user.password)
    )
    try:
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        logger.info(f"User: {user.email} created successfully.")
        return db_user
    except IntegrityError:
        db.rollback()
        logger.warning(f"User with email {user.email} already exists.")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"User with email {user.email} already exists."
        )

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
    payload = decode_access_token(refresh_token)
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

def get_user_by_id(db: Session, user_id: int):
    """Returns a user described by user_id"""
    return db.query(User).filter(User.id == user_id).first()

def get_user_by_email(db: Session, email: EmailStr):
    """Gets a user by email"""
    return db.query(User).filter(User.email == email).first()

def get_all_users(db: Session):
    """Returns all users"""
    return db.query(User).all()

def update_user(db: Session, user_id: int, name: str, email: EmailStr, hased_password: str):
    """Updates user with new details"""
    user = db.query(User).filter(User.id == user_id).first()