from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import BaseDB

if TYPE_CHECKING:
    from app.models.place import PlaceDB


class ProjectDB(BaseDB):
    name: Mapped[str] = mapped_column(nullable=False)
    description: Mapped[str | None] = mapped_column(nullable=True)
    start_date: Mapped[datetime | None] = mapped_column(DateTime, default=datetime.now)

    places: Mapped[list["PlaceDB"]] = relationship(
        back_populates="project", cascade="all, delete-orphan"
    )

    @property
    def is_completed(self) -> bool:
        if not self.places:
            return False
        return all(place.is_visited for place in self.places)
