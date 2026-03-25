from typing import Any, Dict, Generic, List, Optional, Type, TypeVar, Union
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.base import BaseDB

ModelType = TypeVar("ModelType", bound=BaseDB)
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)


class CRUDBase(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    def __init__(self, model: Type[ModelType]):
        self.model = model

    async def get(
        self, db: AsyncSession, id: Any, relationships: list[str] | None = None
    ) -> ModelType | list[ModelType] | None:
        query = select(self.model).where(self.model.id == id)

        if relationships:
            for relationship in relationships:
                query = query.options(selectinload(getattr(self.model, relationship)))

        result = await db.execute(query)
        return result.scalar_one_or_none()

    async def get_multi(
        self,
        db: AsyncSession,
        *,
        offset: int = 0,
        limit: int = 100,
        relationships: list[str],
    ) -> List[ModelType]:
        query = select(self.model).offset(offset).limit(limit)

        if relationships:
            for relationship in relationships:
                query = query.options(selectinload(getattr(self.model, relationship)))

        result = await db.execute(query)
        return list(result.scalars().all())

    async def create(self, db: AsyncSession, *, obj_in: CreateSchemaType) -> ModelType:
        obj_in_data = obj_in.model_dump()
        db_obj = self.model(**obj_in_data)  # type: ignore

        db.add(db_obj)
        await db.commit()
        return db_obj

    async def update(
        self,
        db: AsyncSession,
        *,
        db_obj: ModelType,
        obj_in: Union[UpdateSchemaType, Dict[str, Any]],
    ) -> ModelType:
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.model_dump(exclude_unset=True)

        for field, value in update_data.items():
            if hasattr(db_obj, field):
                setattr(db_obj, field, value)

        db.add(db_obj)
        await db.commit()
        return db_obj

    async def remove(self, db: AsyncSession, *, id: int) -> Optional[ModelType]:
        obj = await self.get(db=db, id=id)
        if not obj:
            raise ValueError(f"{self.model.__name__} {id} not found")
        await db.delete(obj)
        await db.commit()
        return obj
