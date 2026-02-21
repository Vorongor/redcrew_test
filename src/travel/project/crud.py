from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from typing import List

from src.database.models import TravelProjectModel, PlaceModel
from src.travel.place.exceptions import (
    ProjectLimitReachedError,
    PlaceAlreadyExistsInProjectError,
    InvalidExternalPlaceError
)
from src.travel.project.exceptions import (
    ProjectDoesNotExistError,
    ProjectHasVisitedPlacesError
)
from src.travel.schemas import TravelProjectCreate, TravelProjectUpdate
from src.travel.services import validate_external_place


async def _get_project_by_id(
        db: AsyncSession,
        project_id: int,
        load_places: bool = True
) -> TravelProjectModel:
    """
    Internal helper to fetch project.
    load_places=True uses selectinload to avoid LazyLoading errors.
    """
    query = select(TravelProjectModel).where(
        TravelProjectModel.id == project_id)

    if load_places:
        query = query.options(selectinload(TravelProjectModel.places))

    result = await db.execute(query)
    project = result.scalar_one_or_none()

    if not project:
        raise ProjectDoesNotExistError()
    return project


async def create_project(
        db: AsyncSession,
        project_data: TravelProjectCreate
) -> TravelProjectModel:
    if project_data.places:
        if len(project_data.places) > 10:
            raise ProjectLimitReachedError()

        ids = [p.external_id for p in project_data.places]
        if len(ids) != len(set(ids)):
            raise PlaceAlreadyExistsInProjectError()

        for place in project_data.places:
            if not await validate_external_place(place.external_id):
                raise InvalidExternalPlaceError(
                    f"ID {place.external_id} is invalid")

    new_project = TravelProjectModel(
        name=project_data.name,
        description=project_data.description,
        start_date=project_data.start_date
    )

    if project_data.places:
        new_project.places = [
            PlaceModel(**place.model_dump()) for place in project_data.places
        ]

    db.add(new_project)
    await db.commit()

    await db.refresh(new_project, ["places"])
    return new_project


async def get_projects(
        db: AsyncSession, skip: int = 0, limit: int = 100
) -> List[TravelProjectModel]:
    query = (
        select(TravelProjectModel)
        .options(selectinload(TravelProjectModel.places))
        .offset(skip)
        .limit(limit)
    )
    result = await db.execute(query)
    return list(result.scalars().all())


async def get_project_by_id(
        db: AsyncSession, project_id: int
) -> TravelProjectModel:
    return await _get_project_by_id(db, project_id, load_places=True)


async def update_project(
        db: AsyncSession,
        project_id: int,
        update_data: TravelProjectUpdate
) -> TravelProjectModel:
    project = await _get_project_by_id(db, project_id)

    data = update_data.model_dump(exclude_unset=True)
    for key, value in data.items():
        setattr(project, key, value)

    await db.commit()
    await db.refresh(project, ["places"])
    return project


async def delete_project(db: AsyncSession, project_id: int) -> bool:
    project = await _get_project_by_id(db, project_id, load_places=True)

    if any(place.is_visited for place in project.places):
        raise ProjectHasVisitedPlacesError()

    await db.delete(project)
    await db.commit()
    return True
