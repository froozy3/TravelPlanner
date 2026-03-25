from datetime import date

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.schemas.place import PlaceRead


class ProjectBase(BaseModel):
    name: str
    description: str | None
    start_date: date | None


class ProjectCreate(ProjectBase):
    places_ids: list[int] = Field(
        min_length=1,
        max_length=10,
        description="Required: 1–10 Art Institute artwork ids (external place ids).",
    )

    @field_validator("places_ids")
    @classmethod
    def validate_unique_ids(cls, v: list[int]) -> list[int]:
        if len(v) != len(set(v)):
            raise ValueError("Duplicate place IDs are not allowed in a single project")
        return v


class ProjectUpdate(BaseModel):
    name: str | None
    description: str | None
    start_date: date | None


class ProjectRead(ProjectBase):
    id: int
    is_completed: bool
    places: list[PlaceRead]

    model_config = ConfigDict(from_attributes=True)
