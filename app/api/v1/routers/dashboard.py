from http.client import HTTPException
from typing import Annotated
from fastapi import Depends, APIRouter
from fastapi.security import OAuth2PasswordRequestForm
from sqlmodel import select
from app.api.models.user import UserCreate, UserResponse, User
from app.api.dependencies import SessionDep, UserDep, login_for_access_token
from app.utils.jwt import Token
from app.utils.hashing import pwd_context


router = APIRouter(
    prefix="/dashboard",
    tags=["User Panel"]
)

#user create
@router.post("/signup")
async def create_user(new_user: UserCreate, session: SessionDep):
    statement = select(User).where(User.username == new_user.username)
    result = await session.execute(statement)
    user_result = result.scalars().first()

    if user_result:
        raise HTTPException(status_code=409, detail="Username already exists!")

    statement = select(User).where(User.email == new_user.email)
    result = await session.execute(statement)
    email_result = result.scalars().first()

    if email_result:
        raise HTTPException(status_code=409, detail="Email already exists!")
    
    if new_user.password != new_user.rewrite_password:
        raise HTTPException(status_code=400, detail="Passwords do not match.")

    new_user = User(**new_user.model_dump(exclude=["password", "rewrite_password"]),
        hashed_password=pwd_context.hash(new_user.password) #hash password before add to db
    )
    session.add(new_user)
    await session.commit()
    await session.refresh(new_user)
    return {"message": "User created", "username": new_user.username, "user_id": new_user.id}


#user login
@router.post("/login", response_model=Token)
async def login(form_data: Annotated[OAuth2PasswordRequestForm, Depends()],db: SessionDep):
    return await login_for_access_token(form_data, db) 


@router.get("/users/me/", response_model=UserResponse)
async def read_users_me(current_user: UserDep):
    return current_user


