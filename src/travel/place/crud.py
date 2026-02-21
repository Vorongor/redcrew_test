from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List

from src.database.models import PlaceModel
from src.travel.place.exceptions import (
    PlaceAlreadyExistsInProjectError,
    ProjectLimitReachedError,
    PlaceDoesNotExistError,
    InvalidExternalPlaceError
)
from src.travel.schemas import PlaceCreate, PlaceUpdate
from src.travel.services import validate_external_place


async def add_place_to_project(
        db: AsyncSession,
        project_id: int,
        place_data: PlaceCreate
) -> PlaceModel:
    if not await validate_external_place(place_data.external_id):
        raise InvalidExternalPlaceError()

    query = select(PlaceModel).where(PlaceModel.project_id == project_id)
    result = await db.execute(query)
    existing_places = result.scalars().all()

    if len(existing_places) >= 10:
        raise ProjectLimitReachedError()

    if any(p.external_id == place_data.external_id for p in existing_places):
        raise PlaceAlreadyExistsInProjectError()

    new_place = PlaceModel(
        **place_data.model_dump(),
        project_id=project_id
    )
    db.add(new_place)
    await db.commit()
    await db.refresh(new_place)
    return new_place


async def get_project_places(db: AsyncSession, project_id: int) -> List[
    PlaceModel]:
    query = select(PlaceModel).where(PlaceModel.project_id == project_id)
    result = await db.execute(query)
    return list(result.scalars().all())


async def get_place_by_id(db: AsyncSession, place_id: int) -> PlaceModel:
    query = select(PlaceModel).where(PlaceModel.id == place_id)
    result = await db.execute(query)
    place = result.scalar_one_or_none()
    if not place:
        raise PlaceDoesNotExistError()
    return place


async def update_project_place(
        db: AsyncSession,
        place_id: int,
        update_data: PlaceUpdate
) -> PlaceModel:
    place = await get_place_by_id(db, place_id)

    data = update_data.model_dump(exclude_unset=True)
    for key, value in data.items():
        setattr(place, key, value)

    await db.commit()
    await db.refresh(place)
    return place
