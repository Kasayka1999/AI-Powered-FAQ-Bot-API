from sqlmodel import SQLModel, Field


class UserBase(SQLModel):
    username: str = Field(index=True, unique=True)
    email: str = Field(unique=True)
    full_name: str | None = None

class User(UserBase, table=True):
    __tablename__ = "users" #name the table users

    id: int | None = Field(default=None, primary_key=True)
    hashed_password: str
    is_active: bool = Field(default=True)
    is_admin: bool = Field(default=False) 
    organization_id: int | None = Field(default=None, foreign_key="organizations.id")

class UserCreate(UserBase):
    password: str  # This will be hashed before storing

class UserResponse(SQLModel):
    username: str