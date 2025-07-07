"""User service - Performs CRUD operations on users"""
from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from pydantic import EmailStr
from typing import Annotated

from .model import User
from .schema import UserRegistration
from ..core.database import get_db
from .utils import hash_password, verify_password
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
    db_user = get_user_by_email(db, email)
    if not db_user or not verify_password(password, db_user.hashed_password):
        return None
    return db_user

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