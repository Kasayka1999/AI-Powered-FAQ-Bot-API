from datetime import datetime
from sqlmodel import Column, Field, Relationship, SQLModel
from sqlalchemy.dialects import postgresql
from uuid import uuid4, UUID
from typing import TYPE_CHECKING, List, Optional
from pgvector.sqlalchemy import Vector

if TYPE_CHECKING:
    from app.models.organization import Organization


class DocumentsBase(SQLModel):
    file_name: str
    upload_by: str
    organization_id: UUID
    uploaded_at: datetime = Field(
        sa_column=Column(
            postgresql.TIMESTAMP,
            default=datetime.now,
        )
    )
    storage_key: str

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
    organization: "Organization" = Relationship(back_populates="documents", sa_relationship_kwargs={"lazy": "selectin"})

    # Track if embeddings are up to date vs upload time
    last_embedded_at: Optional[datetime] = Field(
        default=None,
        sa_column=Column(postgresql.TIMESTAMP, nullable=True)
    )

    # Relationship to chunks
    chunks: List["DocumentChunk"] = Relationship(
        back_populates="document",
        sa_relationship_kwargs={"lazy": "selectin", "cascade": "all, delete-orphan", "passive_deletes": True},
    )


class DocumentChunk(SQLModel, table=True):
    __tablename__ = "document_chunks"
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    document_id: UUID = Field(foreign_key="documents.id", ondelete="CASCADE", nullable=False, index=True)

    # store chunk text as Postgres TEXT 
    content: str = Field(
        sa_column=Column(postgresql.TEXT, nullable=False)
    )

    # Embedding uses pgvector
    embedding: List[float] = Field(sa_column=Column(Vector(768), nullable=False))

    # Relationship back to parent document
    document: "Documents" = Relationship(
        back_populates="chunks",
        sa_relationship_kwargs={"lazy": "selectin", "passive_deletes": True},
    )

from app.models.organization import Organization #fix mapper