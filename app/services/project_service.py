import asyncio
from datetime import date, datetime, time

from fastapi import HTTPException
from sqlalchemy import exists, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.clients.art_institute import ArtInstituteClient
from app.models.place import PlaceDB
from app.models.project import ProjectDB
from app.services.base import CRUDBase
from app.schemas.project import ProjectCreate, ProjectUpdate


class ProjectService:
    def __init__(
        self,
        db: AsyncSession,
        crud_base: CRUDBase[ProjectDB, ProjectCreate, ProjectUpdate],
        art_institute_client: ArtInstituteClient,
    ):
        self.crud_base = crud_base
        self.db = db
        self.art_institute_client = art_institute_client

    async def get(self, id: int) -> ProjectDB | None:
        return await self.crud_base.get(self.db, id, relationships=["places"])

    async def get_multi(
        self,
        *,
        offset: int = 0,
        limit: int = 100,
        name_contains: str | None = None,
        is_completed: bool | None = None,
        start_date_from: date | None = None,
        start_date_to: date | None = None,
    ) -> list[ProjectDB]:
        query = select(ProjectDB)

        if name_contains:
            escaped = (
                name_contains.replace("\\", "\\\\")
                .replace("%", "\\%")
                .replace("_", "\\_")
            )
            query = query.where(ProjectDB.name.ilike(f"%{escaped}%", escape="\\"))

        has_places = exists().where(PlaceDB.project_id == ProjectDB.id)
        has_unvisited = exists().where(
            PlaceDB.project_id == ProjectDB.id,
            PlaceDB.is_visited.is_(False),
        )

        if is_completed is True:
            query = query.where(has_places, ~has_unvisited)
        elif is_completed is False:
            query = query.where(or_(~has_places, has_unvisited))

        if start_date_from is not None:
            query = query.where(
                ProjectDB.start_date >= datetime.combine(start_date_from, time.min)
            )
        if start_date_to is not None:
            query = query.where(
                ProjectDB.start_date <= datetime.combine(start_date_to, time.max)
            )

        query = (
            query.options(selectinload(ProjectDB.places))
            .order_by(ProjectDB.id)
            .offset(offset)
            .limit(limit)
        )
        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def create(self, *, obj_in: ProjectCreate) -> ProjectDB:
        validations_tasks = [
            self.art_institute_client.validate_place(pid)
            for pid in obj_in.places_ids or []
        ]
        results: list[bool] = await asyncio.gather(*validations_tasks)

        for pid, result in zip(obj_in.places_ids, results):
            if not result:
                raise ValueError(f"Place {pid} is not valid")
        project_data = obj_in.model_dump(exclude={"places_ids"})
        project = ProjectDB(**project_data)

        self.db.add(project)
        await self.db.flush()

        for pid in obj_in.places_ids:
            new_place = PlaceDB(external_id=pid, project_id=project.id)
            self.db.add(new_place)

        await self.db.commit()

        return await self.get(project.id)

    async def update(
        self, db: AsyncSession, *, db_obj: ProjectDB, obj_in: ProjectUpdate
    ) -> ProjectDB:
        return await self.crud_base.update(db, db_obj=db_obj, obj_in=obj_in)

    async def remove(self, *, id: int) -> ProjectDB:
        project = await self.get(id)
        if any(place.is_visited for place in project.places):
            raise HTTPException(
                status_code=403, detail="Cannot delete a project with visited places"
            )
        return await self.crud_base.remove(self.db, id=id)
