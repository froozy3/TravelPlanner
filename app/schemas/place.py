from pydantic import BaseModel, ConfigDict


class PlaceBase(BaseModel):
    notes: str | None
    is_visited: bool = False


class PlaceCreate(BaseModel):
    project_id: int
    external_id: int
    notes: str | None = None
    is_visited: bool = False


class PlaceUpdate(BaseModel):
    notes: str | None
    is_visited: bool | None


class PlaceRead(PlaceBase):
    id: int
    external_id: int

    model_config = ConfigDict(from_attributes=True)
