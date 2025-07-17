from datetime import datetime
from sqlmodel import Field, Relationship, SQLModel
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.models.organization import Organization


class DocumentsBase(SQLModel):
    file_name: str 
    upload_by: str
    organization_id: int
    uploaded_at: datetime | None = None

class Documents(DocumentsBase, table=True):
    __tablename__ = "documents"

    id: int | None = Field(default=None, primary_key=True)
    organization_id: int | None = Field(default=None, foreign_key="organizations.id")
    organization: "Organization" = Relationship(back_populates="documents", sa_relationship_kwargs={"lazy":"selectin"})


from app.models.organization import Organization #fix mapper