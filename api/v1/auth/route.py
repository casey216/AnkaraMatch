from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordRequestForm
from typing import Annotated
from sqlalchemy.orm import Session

from api.v1.core.database import get_db
from api.v1.user.service import create_user
from .schema import Token, UserRegistration, UserResponse
from .service import authenticate_user, refresh_access_token

auth = APIRouter(prefix="/auth", tags=["Auth"])

@auth.post("/register", response_model=UserResponse)
def register(user: UserRegistration, db: Annotated[Session, Depends(get_db)]):
    return create_user(user, db)


@auth.post("/login", response_model=Token)
def login(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: Annotated[Session, Depends(get_db)]
):
    return authenticate_user(form_data.username, form_data.password, db)

    
@auth.post("/refresh", response_model=Token)
def refresh_token(request: Request, db: Annotated[Session, Depends(get_db)]):
    refresh_token = request.cookies.get("refresh_token")
    if not refresh_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh Token not found"
        )
    
    return refresh_access_token(db, refresh_access_token)