from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import BaseDB

if TYPE_CHECKING:
    from app.models.project import ProjectDB


class PlaceDB(BaseDB):
    external_id: Mapped[int] = mapped_column(index=True, nullable=False)
    notes: Mapped[str] = mapped_column(nullable=True)
    is_visited: Mapped[bool] = mapped_column(default=False)
    project_id: Mapped[int] = mapped_column(
        ForeignKey("projects.id"), nullable=False
    )

    project: Mapped["ProjectDB"] = relationship(back_populates="places")
