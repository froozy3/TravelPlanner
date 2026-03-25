from datetime import date
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_db, get_project_service
from app.schemas.project import ProjectCreate, ProjectRead, ProjectUpdate
from app.services.project_service import ProjectService

router = APIRouter()


@router.post("/", response_model=ProjectRead, status_code=status.HTTP_201_CREATED)
async def create_project(
    project_in: ProjectCreate,
    service: ProjectService = Depends(get_project_service),
):
    """Create a project; validates place IDs via the Art Institute API."""
    try:
        return await service.create(obj_in=project_in)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/", response_model=list[ProjectRead])
async def list_projects(
    offset: Annotated[int, Query(ge=0, description="Skip this many rows.")] = 0,
    limit: Annotated[int, Query(ge=1, le=500, description="Max rows to return.")] = 100,
    name_contains: Annotated[
        str | None,
        Query(description="Case-insensitive substring match on project name."),
    ] = None,
    is_completed: Annotated[
        bool | None,
        Query(
            description=(
                "Filter by completion: true = at least one place and all visited; "
                "false = no places or some not visited."
            ),
        ),
    ] = None,
    start_date_from: Annotated[
        date | None,
        Query(
            description="Include projects with start_date on or after this day (UTC date).",
        ),
    ] = None,
    start_date_to: Annotated[
        date | None,
        Query(
            description="Include projects with start_date on or before this day (UTC date).",
        ),
    ] = None,
    service: ProjectService = Depends(get_project_service),
):
    """List projects with pagination and optional filters."""
    return await service.get_multi(
        offset=offset,
        limit=limit,
        name_contains=name_contains,
        is_completed=is_completed,
        start_date_from=start_date_from,
        start_date_to=start_date_to,
    )


@router.get("/{id}", response_model=ProjectRead)
async def get_project(
    id: int,
    service: ProjectService = Depends(get_project_service),
):
    """Return a single project by ID."""
    project = await service.get(id=id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project


@router.patch("/{id}", response_model=ProjectRead)
async def update_project(
    id: int,
    project_in: ProjectUpdate,
    service: ProjectService = Depends(get_project_service),
    db: AsyncSession = Depends(get_db),
):
    """Update project fields."""
    project = await service.get(id=id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    return await service.update(db=db, db_obj=project, obj_in=project_in)


@router.delete("/{id}", response_model=ProjectRead)
async def delete_project(
    id: int,
    service: ProjectService = Depends(get_project_service),
):
    """Delete a project; forbidden if any place is marked visited."""
    project = await service.get(id=id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    return await service.remove(id=id)
