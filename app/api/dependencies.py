from datetime import timedelta
from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
import jwt
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from app.api.models.user import User
from app.database.session import get_session
from app.utils.hashing import verify_password
from app.utils.jwt import Token, TokenData, create_access_token, oauth2_scheme
from app.config import security_settings


# Asynchronous database session dep annotation
SessionDep = Annotated[AsyncSession, Depends(get_session)]

async def get_user(session: SessionDep, username: str):
    statement = select(User).where(User.username == username)
    result = await session.execute(statement)
    get_user = result.scalars().first() 
    return get_user

async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)],
                           session: SessionDep):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Not authorized",
    )
    try:
        payload = jwt.decode(token, security_settings.JWT_SECRET, algorithms=[security_settings.JWT_ALGORITHM])
        username = payload.get("user", {}).get("name") #To avoid any key error used .get
        if username is None:
            raise credentials_exception
    except jwt.InvalidTokenError:
        raise credentials_exception

    token_data = TokenData(username=username)
    user = await get_user(session, username=token_data.username)
    if user is None:
        raise credentials_exception
    if not user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return user


async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: SessionDep,
) -> Token:
    user = await get_user(db, form_data.username)

    if user is None or not verify_password(form_data.password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Email or password is incorrect",
            )
    
    access_token_expires = timedelta(minutes=security_settings.JWT_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={
            "user": {
                "name": user.username,
                "id": str(user.id),
            },
        }, expires_delta=access_token_expires)
    return Token(access_token=access_token, token_type="bearer")

#Get authorized user
UserDep = Annotated[User, Depends(get_current_user)]