from typing import List, Annotated
from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.schemas import UserReadSchema
from src.auth.security.utils import get_current_user
from src.database import get_db
from src.travel.project import crud
from src.travel.schemas import (
    TravelProjectCreate,
    TravelProjectUpdate,
    TravelProjectRead
)
from src.travel.project.exceptions import (
    ProjectDoesNotExistError,
    ProjectHasVisitedPlacesError
)

travel_router = APIRouter(prefix="/projects", tags=["Travel Projects"])


@travel_router.post(
    "/",
    response_model=TravelProjectRead,
    status_code=status.HTTP_201_CREATED
)
async def create_travel_project(
        project_in: TravelProjectCreate,
        db: Annotated[AsyncSession, Depends(get_db)],
        auth_user: Annotated[UserReadSchema, Depends(get_current_user)],
):
    """Create a new travel project, optionally with places."""
    return await crud.create_project(db, project_data=project_in)


@travel_router.get("/", response_model=List[TravelProjectRead])
async def list_travel_projects(
        db: Annotated[AsyncSession, Depends(get_db)],
        auth_user: Annotated[UserReadSchema, Depends(get_current_user)],
        skip: int = 0,
        limit: int = 100,
):
    """List all travel projects."""
    return await crud.get_projects(db, skip=skip, limit=limit)


@travel_router.get("/{project_id}", response_model=TravelProjectRead)
async def get_travel_project(
        project_id: int,
        db: Annotated[AsyncSession, Depends(get_db)],
        auth_user: Annotated[UserReadSchema, Depends(get_current_user)],
):
    """Get a single travel project by ID."""
    try:
        return await crud.get_project_by_id(db, project_id=project_id)
    except ProjectDoesNotExistError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )


@travel_router.patch("/{project_id}", response_model=TravelProjectRead)
async def update_travel_project(
        project_id: int,
        project_in: TravelProjectUpdate,
        db: Annotated[AsyncSession, Depends(get_db)],
        auth_user: Annotated[UserReadSchema, Depends(get_current_user)],
):
    """Update travel project details (Name, Description, Start Date)."""
    try:
        return await crud.update_project(
            db, project_id=project_id, update_data=project_in
        )
    except ProjectDoesNotExistError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )


@travel_router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_travel_project(
        project_id: int,
        db: Annotated[AsyncSession, Depends(get_db)],
        auth_user: Annotated[UserReadSchema, Depends(get_current_user)],
):
    """
    Remove a travel project.
    Fails if any places are marked as visited.
    """
    try:
        await crud.delete_project(db, project_id=project_id)
    except ProjectDoesNotExistError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    except ProjectHasVisitedPlacesError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete project: some places are already marked as visited."
        )
