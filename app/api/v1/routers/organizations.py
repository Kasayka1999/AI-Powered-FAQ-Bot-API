from fastapi import APIRouter
from typing import Annotated
from fastapi import Depends, HTTPException
from app.api.models.organization import OrganizationCreate, Organization
from app.database.database import SessionDep
from app.api.models.user import User
from app.utils.jwt import get_current_active_user
from datetime import datetime

router = APIRouter(
    prefix="/organizations",
    tags=["Organizations"]
    )

@router.post("/create", response_model=OrganizationCreate)
async def create_organization(organization: OrganizationCreate, current_user: Annotated[User, Depends(get_current_active_user)], db: SessionDep):
    if current_user.organization_id is not None:
        raise HTTPException(
            status_code=400,
            detail="User already belongs to an organization."
        )
    organization = Organization(
        name=organization.name,
        created_by=current_user.username,
        created_at=datetime.now()
    )
    db.add(organization)
    db.commit()
    db.refresh(organization)

    # Update user's organization_id
    current_user.organization_id = organization.id
    db.add(current_user)
    db.commit()
    db.refresh(current_user)

    return organization