from fastapi import APIRouter, Depends, status

from app.api.dependencies import get_place_service
from app.schemas.place import PlaceCreate, PlaceRead, PlaceUpdate
from app.services.place_service import PlaceService

router = APIRouter()


@router.post("/", response_model=PlaceRead, status_code=status.HTTP_201_CREATED)
async def add_place_to_project(
    place_in: PlaceCreate,
    service: PlaceService = Depends(get_place_service),
):
    """Add a place to a project after museum API validation."""
    return await service.add_to_project(place_in.project_id, place_in)


@router.get("/project/{project_id}", response_model=list[PlaceRead])
async def list_project_places(
    project_id: int,
    service: PlaceService = Depends(get_place_service),
):
    """List all places belonging to a project."""
    return await service.list_for_project(project_id)


@router.patch("/{place_id}", response_model=PlaceRead)
async def update_place(
    place_id: int,
    place_in: PlaceUpdate,
    service: PlaceService = Depends(get_place_service),
):
    """Update place notes and/or visited flag."""
    return await service.update(place_id, place_in)


@router.delete("/{place_id}", response_model=PlaceRead)
async def delete_place(
    place_id: int,
    service: PlaceService = Depends(get_place_service),
):
    """Remove a place from its project."""
    return await service.remove(place_id)


@router.get("/{place_id}", response_model=PlaceRead)
async def get_place(place_id: int, service: PlaceService = Depends(get_place_service)):
    """Return one place by ID."""
    return await service.get_by_id(place_id)
