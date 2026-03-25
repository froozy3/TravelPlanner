from typing import AsyncGenerator
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.clients.art_institute import art_client
from app.db.session import AsyncSessionLocal
from app.models.place import PlaceDB
from app.models.project import ProjectDB
from app.schemas.place import PlaceUpdate
from app.schemas.project import ProjectCreate, ProjectUpdate
from app.services.base import CRUDBase
from app.services.place_service import PlaceService
from app.services.project_service import ProjectService
from app.schemas.place import PlaceCreate


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def get_project_service(db: AsyncSession = Depends(get_db)) -> ProjectService:
    crud_project = CRUDBase[ProjectDB, ProjectCreate, ProjectUpdate](ProjectDB)
    return ProjectService(
        db=db, crud_base=crud_project, art_institute_client=art_client
    )


async def get_place_service(db: AsyncSession = Depends(get_db)) -> PlaceService:
    crud_place = CRUDBase[PlaceDB, PlaceCreate, PlaceUpdate](PlaceDB)
    return PlaceService(db=db, crud=crud_place)
