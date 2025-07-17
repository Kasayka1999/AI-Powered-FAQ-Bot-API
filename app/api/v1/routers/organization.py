from fastapi import APIRouter
from typing import Annotated
from fastapi import Depends, HTTPException
from sqlmodel import select
from app.models.organization import OrganizationCreate, Organization, OrganizationDelete
from app.api.dependencies import SessionDep, UserDep
from datetime import datetime

router = APIRouter(
    prefix="/organization",
    tags=["Organization"]
    )

@router.post("/create")
async def create_organization(new_organization: OrganizationCreate, current_user: UserDep, session: SessionDep):
    if current_user.organization_id is not None:
        raise HTTPException(
            status_code=400,
            detail="User already belongs to an organization."
        )
    
    if not new_organization.organization_name or new_organization.organization_name.strip() == "":
        raise HTTPException(status_code=400, detail="Please enter organization name")
    
    new_organization = Organization(
        organization_name=new_organization.organization_name,
        created_by=current_user.username,
        created_at=datetime.now()
    )
    session.add(new_organization)
    await session.commit()
    await session.refresh(new_organization)

    # Update user's organization_id
    current_user.organization_id = new_organization.id
    await session.commit()
    await session.refresh(current_user)

    return {"message": "Organization created successfully!", "organization_name": new_organization.organization_name}


@router.delete("/delete/")
async def delete_organization(delete_organization: OrganizationDelete, current_user: UserDep, session: SessionDep):
    if not current_user.organization:
        raise HTTPException(status_code=400, detail="You don't have organization")
    
    if not delete_organization.organization_name == current_user.organization.organization_name:
        raise HTTPException(status_code=400, detail="Please type your organization name, in case if you forget check dashboard / User Info")
    
    statement = select(Organization).where(Organization.organization_name == delete_organization.organization_name)
    result = await session.execute(statement)
    organization_result = result.scalars().first()
    
    await session.delete(organization_result)
    await session.commit()
    
    return {"message": "Successfully organization deleted.", "organization_name": delete_organization.organization_name}