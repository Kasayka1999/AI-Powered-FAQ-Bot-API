from typing import Annotated
from fastapi import Depends, APIRouter
from fastapi.security import OAuth2PasswordRequestForm
from app.utils.jwt import login_for_access_token
from app.api.models.user import UserResponse, User
from app.database.database import SessionDep
from app.utils.jwt import get_current_active_user, Token


router = APIRouter(
    prefix="/login",
    tags=["Login"]
)


@router.post("/token", response_model=Token)
async def login(form_data: Annotated[OAuth2PasswordRequestForm, Depends()],db: SessionDep):
    return await login_for_access_token(form_data, db) #when calling an async def function from another async def, always use await.


@router.get("/users/me/", response_model=UserResponse)
async def read_users_me(
    current_user: Annotated[User, Depends(get_current_active_user)],
):
    return current_user


