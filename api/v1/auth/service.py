"""User service - Performs CRUD operations on users"""
from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from pydantic import EmailStr
from typing import Annotated

from .model import User
from .schema import UserRegistration
from ..core.database import get_db
from .utils import hash_password


def create_user(user: UserRegistration, db: Annotated[Session, Depends(get_db)]):
    """Creates new user"""
    db_user = User(
        name=user.name,
        email=user.email,
        hashed_password=hash_password(user.password)
    )
    try:
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return db_user
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"User with email {user.email} already exists."
        )

def get_user(db: Session, user_id: int):
    """Returns a user described by user_id"""
    user = db.query(User).filter(User.id == user_id).first()
    return user

def get_all_users(db: Session):
    """Returns all users"""
    users = db.query(User).all()
    return users

def update_user(db: Session, user_id: int, name: str, email: EmailStr, hased_password: str):
    """Updates user with new details"""
    user = db.query(User).filter(User.id == user_id).first()