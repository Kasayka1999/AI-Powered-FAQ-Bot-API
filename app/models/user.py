from sqlmodel import Column, Relationship, SQLModel, Field
from pydantic import EmailStr
from sqlalchemy.dialects import postgresql
from uuid import uuid4, UUID
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.models.organization import Organization


class UserBase(SQLModel):
    username: str = Field(index=True, unique=True)
    email: EmailStr
    full_name: str | None = None

class User(UserBase, table=True):
    __tablename__ = "users" #name the table users

    id: UUID = Field(
        sa_column=Column(
            postgresql.UUID,
            default=uuid4,
            primary_key=True,
        )
    )
    hashed_password: str
    is_active: bool = Field(default=True)
    is_admin: bool = Field(default=False) 
    organization_id: UUID | None = Field(default=None, foreign_key="organizations.id")
    organization: "Organization" = Relationship(back_populates="user", sa_relationship_kwargs={"lazy": "selectin", "uselist": False})

class UserCreate(UserBase):
    password: str  # This will be hashed before storing
    rewrite_password: str

class UserResponse(SQLModel):
    username: str
    email: EmailStr
    full_name: str
    organization: str | None