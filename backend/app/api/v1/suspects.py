from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.api import deps
from app.models.user import User
from app.schemas.suspect import Suspect, SuspectCreate, SuspectUpdate
from app.models.entities import Suspect as SuspectModel
from app.repositories.base import BaseRepository

router = APIRouter()

suspect_repo = BaseRepository(SuspectModel)

@router.get("/", response_model=List[Suspect])
def read_suspects(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Retrieve suspects.
    """
    suspects = suspect_repo.get_multi(db, skip=skip, limit=limit)
    return suspects

@router.post("/", response_model=Suspect)
def create_suspect(
    *,
    db: Session = Depends(deps.get_db),
    suspect_in: SuspectCreate,
    current_user: User = Depends(deps.RoleChecker(["OFFICER", "ADMIN"])),
) -> Any:
    """
    Create new suspect record.
    """
    suspect = suspect_repo.create(db, obj_in=suspect_in.dict())
    return suspect

from uuid import UUID

@router.get("/{id}", response_model=Suspect)
def read_suspect(
    *,
    db: Session = Depends(deps.get_db),
    id: UUID,
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get suspect by ID.
    """
    suspect = suspect_repo.get(db, id=id)
    if not suspect:
        raise HTTPException(status_code=404, detail="Suspect not found")
    return suspect

@router.put("/{id}", response_model=Suspect)
def update_suspect(
    *,
    db: Session = Depends(deps.get_db),
    id: UUID,
    suspect_in: SuspectUpdate,
    current_user: User = Depends(deps.RoleChecker(["OFFICER", "ADMIN"])),
) -> Any:
    """
    Update suspect record.
    """
    suspect = suspect_repo.get(db, id=id)
    if not suspect:
        raise HTTPException(status_code=404, detail="Suspect not found")
    suspect = suspect_repo.update(db, db_obj=suspect, obj_in=suspect_in.dict(exclude_unset=True))
    return suspect
