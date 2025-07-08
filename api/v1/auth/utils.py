from datetime import datetime, timedelta, timezone

from passlib.context import CryptContext
from jose import jwt, JWTError
from jose.exceptions import ExpiredSignatureError

from ..core.settings import settings


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    to_encode = data.copy()
    created_time = datetime.now(timezone.utc)
    expire = created_time + (expires_delta or timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire, "iat": created_time})
    return jwt.encode(to_encode,settings.JWT_SECRET,algorithm=settings.ALGORITHM)

def create_refresh_token(data: dict):
    create_access_token(data, expires_delta=timedelta(days=7))

def decode_access_token(token: str) -> dict:
    try:
        return jwt.decode(
            token,
            settings.JWT_SECRET,
            algorithms=[settings.ALGORITHM]
        ), None
    except ExpiredSignatureError:
        return None, "Token expired."
    except JWTError:
        return None, "Invalid token."


