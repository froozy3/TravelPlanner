from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from app.clients.art_institute import art_client
from app.models.place import PlaceDB
from app.models.project import ProjectDB
from app.schemas.place import PlaceCreate, PlaceUpdate
from app.services.base import CRUDBase


class PlaceService:
    def __init__(self, db: AsyncSession, crud: CRUDBase[PlaceDB, PlaceCreate, PlaceUpdate]):
        self.db = db
        self.crud = crud

    async def add_to_project(self, project_id: int, obj_in: PlaceCreate) -> PlaceDB:
        query = select(ProjectDB).options(selectinload(ProjectDB.places)).where(ProjectDB.id == project_id)
        result = await self.db.execute(query)
        project = result.scalar_one_or_none()

        if not project:
            raise HTTPException(status_code=404, detail="Project not found")

        if len(project.places) >= 10:
            raise HTTPException(status_code=400, detail="Project already has maximum (10) places")

        if any(p.external_id == obj_in.external_id for p in project.places):
            raise HTTPException(status_code=400, detail="This place is already in the project")

        is_valid = await art_client.validate_place(obj_in.external_id)
        if not is_valid:
            raise HTTPException(status_code=400, detail="Invalid external_id: Place not found in Art Institute API")

        new_place = PlaceDB(
            external_id=obj_in.external_id,
            project_id=project_id,
            notes=obj_in.notes,
            is_visited=obj_in.is_visited
        )
        self.db.add(new_place)
        await self.db.commit()
        await self.db.refresh(new_place)
        return new_place

    async def get_by_id(self, place_id: int) -> PlaceDB:
        place = await self.crud.get(self.db, id=place_id)
        if not place:
            raise HTTPException(status_code=404, detail="Place not found")
        return place

    async def update(self, place_id: int, obj_in: PlaceUpdate) -> PlaceDB:
        db_obj = await self.get_by_id(place_id)
        return await self.crud.update(self.db, db_obj=db_obj, obj_in=obj_in)

    async def list_for_project(self, project_id: int) -> list[PlaceDB]:
        q = (
            select(PlaceDB)
            .where(PlaceDB.project_id == project_id)
            .order_by(PlaceDB.id)
        )
        result = await self.db.execute(q)
        return list(result.scalars().all())

    async def remove(self, place_id: int) -> PlaceDB:
        db_obj = await self.get_by_id(place_id)
        await self.db.delete(db_obj)
        await self.db.commit()
        return db_obj
