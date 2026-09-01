from datetime import timedelta
from typing import Any
from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from pydantic import BaseModel
import time

from app.api import deps
from app.core import security
from app.core.config import settings
from app.models.user import User

router = APIRouter()

LOGIN_ATTEMPTS = {}

class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str

class Msg(BaseModel):
    msg: str

@router.post("/login", response_model=Token)
def login_access_token(
    request: Request,
    db: Session = Depends(deps.get_db), form_data: OAuth2PasswordRequestForm = Depends()
) -> Any:
    client_ip = request.client.host if request.client else "unknown"
    now = time.time()
    
    # Simple rate limiting: max 5 attempts per minute per IP
    if client_ip in LOGIN_ATTEMPTS:
        attempts, last_time = LOGIN_ATTEMPTS[client_ip]
        if now - last_time < 60:
            if attempts >= 5:
                raise HTTPException(status_code=429, detail="Too many login attempts. Please try again later.")
            LOGIN_ATTEMPTS[client_ip] = (attempts + 1, last_time)
        else:
            LOGIN_ATTEMPTS[client_ip] = (1, now)
    else:
        LOGIN_ATTEMPTS[client_ip] = (1, now)

    """
    OAuth2 compatible token login, get an access token for future requests.
    """
    user = db.query(User).filter(User.badge_number == form_data.username, User.is_deleted == False).first()
    if not user or not security.verify_password(form_data.password, user.password_hash):
        raise HTTPException(status_code=400, detail="Incorrect badge number or password")
    elif not user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
        
    # MFA readiness check can be inserted here if required
    
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = security.create_access_token(
        user.id, expires_delta=access_token_expires
    )
    refresh_token = security.create_refresh_token(user.id)
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
    }

@router.post("/refresh", response_model=Token)
def refresh_token(
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """
    Refresh access token
    """
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = security.create_access_token(
        current_user.id, expires_delta=access_token_expires
    )
    refresh_token = security.create_refresh_token(current_user.id)
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
    }
