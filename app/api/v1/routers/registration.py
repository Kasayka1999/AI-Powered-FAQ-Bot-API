from http.client import HTTPException

from fastapi import APIRouter, HTTPException
from passlib.context import CryptContext
from sqlmodel import select
from app.api.models.user import UserCreate, User
from app.api.dependencies import SessionDep


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

router = APIRouter(
    prefix="/register",
    tags=["Registration"]
)

@router.post("/create")
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