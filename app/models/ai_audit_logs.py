from typing import Optional
from uuid import uuid4
from datetime import datetime
from sqlmodel import Relationship, SQLModel, Field
from uuid import uuid4, UUID
from sqlalchemy import Column
from sqlalchemy.dialects import postgresql
from typing import List

from app.models.organization import Organization

class AIAuditLogs(SQLModel, table=True):
    __tablename__ = "ai_audit_logs"

    id: UUID = Field(
        sa_column=Column(
            postgresql.UUID,
            default=uuid4,
            primary_key=True,
        )
    )
    # organization required: every audit row must belong to an organization
    organization_id: UUID | None = Field(default=None, foreign_key="organizations.id", index=True)
    #Relationship organization - logs
    organization: "Organization" = Relationship(back_populates="logs", sa_relationship_kwargs={"lazy": "selectin"})
    
    requester_email: Optional[str] = Field(default=None)
    requester_full_name: Optional[str] = Field(default=None)
    
    prompt: Optional[str] = Field(default=None, sa_column=Column(postgresql.TEXT, nullable=True))
    response_text: Optional[str] = Field(default=None, sa_column=Column(postgresql.TEXT, nullable=True))

    input_tokens: Optional[int] = Field(default=None, index=True)
    output_tokens: Optional[int] = Field(default=None)
    total_tokens: Optional[int] = Field(default=None, index=True)
    model_name: Optional[str] = Field(default=None)
    sources: Optional[dict] = Field(default=None, sa_column=Column(postgresql.JSONB, nullable=True))


    requested_at: datetime = Field(default_factory=datetime.utcnow, sa_column=Column(postgresql.TIMESTAMP, nullable=False))