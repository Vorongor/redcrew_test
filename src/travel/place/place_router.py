from typing import List, Annotated
from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import get_db
from src.travel.place.crud import (
    add_place_to_project,
    get_project_places,
    get_place_by_id,
    update_project_place
)
from src.travel.schemas import PlaceRead, PlaceCreate, PlaceUpdate
from src.travel.place.exceptions import (
    ProjectLimitReachedError,
    PlaceAlreadyExistsInProjectError,
    InvalidExternalPlaceError,
    PlaceDoesNotExistError
)

places_router = APIRouter(tags=["Places"])


@places_router.post(
    "/projects/{project_id}/places",
    response_model=PlaceRead,
    status_code=status.HTTP_201_CREATED
)
async def add_place(
        project_id: int,
        place_in: PlaceCreate,
        db: Annotated[AsyncSession, Depends(get_db)]
):
    """Add a validated Art Institute place to an existing project."""
    try:
        return await add_place_to_project(
            db, project_id=project_id, place_data=place_in
        )
    except InvalidExternalPlaceError:
        raise HTTPException(
            status_code=400,
            detail="External ID not found in Art Institute API"
        )
    except ProjectLimitReachedError:
        raise HTTPException(
            status_code=400,
            detail="Project already has the maximum of 10 places"
        )
    except PlaceAlreadyExistsInProjectError:
        raise HTTPException(
            status_code=400,
            detail="This place is already in the project"
        )


@places_router.get("/projects/{project_id}/places",
                   response_model=List[PlaceRead])
async def list_places(
        project_id: int,
        db: Annotated[AsyncSession, Depends(get_db)]
):
    """List all places for a specific project."""
    return await get_project_places(db, project_id=project_id)



@places_router.get("/places/{place_id}", response_model=PlaceRead)
async def get_place(
        place_id: int,
        db: Annotated[AsyncSession, Depends(get_db)]
):
    """Get details for a single place."""
    try:
        return await get_place_by_id(db, place_id=place_id)
    except PlaceDoesNotExistError:
        raise HTTPException(status_code=404, detail="Place not found")


@places_router.patch("/places/{place_id}", response_model=PlaceRead)
async def update_place(
        place_id: int,
        place_in: PlaceUpdate,
        db: Annotated[AsyncSession, Depends(get_db)]
):
    """Update notes or visited status for a place."""
    try:
        return await update_project_place(
            db, place_id=place_id, update_data=place_in
        )
    except PlaceDoesNotExistError:
        raise HTTPException(status_code=404, detail="Place not found")
