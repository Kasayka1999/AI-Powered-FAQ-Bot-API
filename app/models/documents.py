from datetime import datetime
from sqlmodel import Column, Field, Relationship, SQLModel
from sqlalchemy.dialects import postgresql
from uuid import uuid4, UUID
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.models.organization import Organization


class DocumentsBase(SQLModel):
    file_name: str 
    upload_by: str
    organization_id: int
    uploaded_at: datetime = Field(
        sa_column=Column(
            postgresql.TIMESTAMP,
            default=datetime.now,
        )
    )

class Documents(DocumentsBase, table=True):
    __tablename__ = "documents"

    id: UUID = Field(
        sa_column=Column(
            postgresql.UUID,
            default=uuid4,
            primary_key=True,
        )
    )
    organization_id: UUID | None = Field(default=None, foreign_key="organizations.id")
    organization: "Organization" = Relationship(back_populates="documents", sa_relationship_kwargs={"lazy":"selectin"})


from app.models.organization import Organization #fix mapper