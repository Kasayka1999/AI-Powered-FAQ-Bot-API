from sqlmodel import Column, Field, Relationship, SQLModel
from sqlalchemy.dialects import postgresql
from uuid import uuid4, UUID
from datetime import datetime
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.models.user import User
    from app.models.documents import Documents

class OrganizationBase(SQLModel):
    organization_name: str = Field(index=True, unique=True)
    created_by: str | None = None
    created_at: datetime = Field(
        sa_column=Column(
            postgresql.TIMESTAMP,
            default=datetime.now,
        )
    )

class Organization(OrganizationBase, table=True):
    __tablename__ = "organizations"  # name the table organizations

    id: UUID = Field(
        sa_column=Column(
            postgresql.UUID,
            default=uuid4,
            primary_key=True,
        )
    )
    user: "User" = Relationship(back_populates="organization", sa_relationship_kwargs={"lazy": "selectin", "uselist": False})
    documents: "Documents" = Relationship(back_populates="organization", sa_relationship_kwargs={"lazy": "selectin"})

class OrganizationCreate(SQLModel):
    organization_name: str

class OrganizationDelete(OrganizationCreate):
    pass




from app.models.documents import Documents #fix mapping error