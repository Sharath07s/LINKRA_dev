from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.models.user import User as UserModel
from app.schemas.user import User, UserCreate, UserUpdate
from app.api import deps
from app.core.security import get_password_hash
from app.repositories.base import BaseRepository

router = APIRouter()
user_repo = BaseRepository(UserModel)

@router.get("/me", response_model=User)
def read_user_me(
    current_user: UserModel = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get current user.
    """
    return current_user

@router.get("/", response_model=List[User])
def read_users(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: UserModel = Depends(deps.RoleChecker(["ADMIN"])),
) -> Any:
    """
    Retrieve users. Only admins can view all users.
    """
    users = user_repo.get_multi(db, skip=skip, limit=limit)
    return users

@router.post("/", response_model=User)
def create_user(
    *,
    db: Session = Depends(deps.get_db),
    user_in: UserCreate,
    current_user: UserModel = Depends(deps.RoleChecker(["ADMIN"])),
) -> Any:
    """
    Create new user.
    """
    user = db.query(UserModel).filter(UserModel.badge_number == user_in.badge_number).first()
    if user:
        raise HTTPException(
            status_code=400,
            detail="The user with this badge number already exists in the system.",
        )
    user = db.query(UserModel).filter(UserModel.email == user_in.email).first()
    if user and user_in.email:
        raise HTTPException(
            status_code=400,
            detail="The user with this email already exists in the system.",
        )
    
    obj_in_data = user_in.dict(exclude={"password"})
    obj_in_data["password_hash"] = get_password_hash(user_in.password)
    user = user_repo.create(db, obj_in=obj_in_data)
    return user

from uuid import UUID

@router.put("/{id}", response_model=User)
def update_user(
    *,
    db: Session = Depends(deps.get_db),
    id: UUID,
    user_in: UserUpdate,
    current_user: UserModel = Depends(deps.RoleChecker(["ADMIN"])),
) -> Any:
    """
    Update a user.
    """
    user = user_repo.get(db, id=id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
        
    update_data = user_in.dict(exclude_unset=True)
    if "password" in update_data:
        update_data["password_hash"] = get_password_hash(update_data.pop("password"))
        
    user = user_repo.update(db, db_obj=user, obj_in=update_data)
    return user

@router.delete("/{id}", response_model=User)
def deactivate_user(
    *,
    db: Session = Depends(deps.get_db),
    id: UUID,
    current_user: UserModel = Depends(deps.RoleChecker(["ADMIN"])),
) -> Any:
    """
    Deactivate a user instead of deleting.
    """
    user = user_repo.get(db, id=id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    user = user_repo.update(db, db_obj=user, obj_in={"is_active": False})
    return user

@router.get("/admin-only", response_model=dict)
def read_admin_data(
    current_user: UserModel = Depends(deps.RoleChecker(["ADMIN"])),
) -> Any:
    """
    Only SCRB Admin can access this route.
    """
    return {"msg": "Welcome Admin"}
