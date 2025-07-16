from fastapi.security import OAuth2PasswordBearer
import jwt
from sqlmodel import SQLModel
from datetime import datetime, timedelta, timezone
from app.config import security_settings


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/dashboard/login")

class Token(SQLModel):
    access_token: str
    token_type: str


class TokenData(SQLModel):
    username: str | None = None


def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15) #default value, in case not receive value
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, security_settings.JWT_SECRET, algorithm=security_settings.JWT_ALGORITHM)
    return encoded_jwt

