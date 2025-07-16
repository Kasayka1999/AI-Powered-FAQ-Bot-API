from sqlmodel import Field, Relationship, SQLModel
from datetime import datetime
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.api.models.user import User

class OrganizationBase(SQLModel):
    name_organization: str = Field(index=True, unique=True)
    created_by: str | None = None
    created_at: datetime | None = None

class Organization(OrganizationBase, table=True):
    __tablename__ = "organizations"  # name the table organizations

    id: int | None = Field(default=None, primary_key=True)
    user: "User" = Relationship(back_populates="organization", sa_relationship_kwargs={"uselist": False})

class OrganizationCreate(SQLModel):
    name: str