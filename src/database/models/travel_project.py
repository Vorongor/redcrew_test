from datetime import date
from typing import List, Optional

from sqlalchemy import String, DateTime, ForeignKey, Text, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.database import Base


class TravelProjectModel(Base):
    __tablename__ = "travel_projects"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(
        Text, nullable=True
    )
    start_date: Mapped[Optional[date]] = mapped_column(
        DateTime, nullable=True
    )

    places: Mapped[List["PlaceModel"]] = relationship(
        "PlaceModel",
        back_populates="project",
        cascade="all, delete-orphan",
    )


class PlaceModel(Base):
    __tablename__ = "places"

    id: Mapped[int] = mapped_column(primary_key=True)
    external_id: Mapped[str] = mapped_column(
        String(255), nullable=False, index=True
    )
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    is_visited: Mapped[bool] = mapped_column(Boolean, default=False)

    project_id: Mapped[int] = mapped_column(
        ForeignKey("travel_projects.id", ondelete="CASCADE"),
        nullable=False
    )

    project: Mapped["TravelProjectModel"] = relationship(
        "TravelProjectModel", back_populates="places"
    )
