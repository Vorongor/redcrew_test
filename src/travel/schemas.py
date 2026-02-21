from datetime import date
from typing import List, Optional
from pydantic import BaseModel, ConfigDict, Field


class PlaceBase(BaseModel):
    external_id: str = Field(..., description="ID from the third-party API")
    notes: Optional[str] = None


class PlaceCreate(PlaceBase):
    pass


class PlaceUpdate(BaseModel):
    notes: Optional[str] = None
    is_visited: Optional[bool] = None


class PlaceRead(PlaceBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    is_visited: bool
    project_id: int


class TravelProjectBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    start_date: Optional[date] = None


class TravelProjectCreate(TravelProjectBase):
    places: List[PlaceCreate] = []


class TravelProjectUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    start_date: Optional[date] = None


class TravelProjectRead(TravelProjectBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    places: List[PlaceRead] = []
