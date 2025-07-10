from http.client import HTTPException

from fastapi import APIRouter, HTTPException
from passlib.context import CryptContext
from app.models.user import User
from app.schemas.user import UserCreate
from app.database.database import SessionDep


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

router = APIRouter(
    prefix="/register",
    tags=["Registration"]
)

@router.post("/create")
async def create_user(user: UserCreate, session: SessionDep):
    if session.query(User).filter(User.username == user.username).first():
        raise HTTPException(status_code=409, detail="Username already exists!")

    if session.query(User).filter(User.email == user.email).first():
        raise HTTPException(status_code=409, detail="Email already exists!")

    hashed_password = pwd_context.hash(user.password)
    user = User(
        username=user.username,
        email=user.email,
        full_name=user.full_name,
        hashed_password=hashed_password
    )
    session.add(user)
    session.commit()
    session.refresh(user)
    return {"message": "User created", "user_id": user.id}