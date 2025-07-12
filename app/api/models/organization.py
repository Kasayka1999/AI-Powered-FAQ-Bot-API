from sqlmodel import Field, SQLModel
from datetime import datetime

class OrganizationBase(SQLModel):
    name: str = Field(index=True, unique=True)
    created_by: str | None = None
    created_at: datetime | None = None

class Organization(OrganizationBase, table=True):
    __tablename__ = "organizations"  # name the table organizations

    id: int | None = Field(default=None, primary_key=True)

class OrganizationCreate(SQLModel):
    name: str