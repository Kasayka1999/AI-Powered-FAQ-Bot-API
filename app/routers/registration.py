from fastapi import APIRouter, Depends
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from app.schemas import UserRequest
from app.models import User
from app.database import get_db


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

router = APIRouter(
    prefix="/register",
    tags=["Registration"]
)

@router.post("/create")
async def create_user(user_request: UserRequest, db: Session = Depends(get_db)):
    hashed_password = pwd_context.hash(user_request.password)
    user = User(
        username=user_request.username,
        email=user_request.email,
        full_name=user_request.full_name,
        hashed_password=hashed_password
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return {"message": "User created", "user_id": user.id}