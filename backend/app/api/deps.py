from typing import Generator, List, Optional
from fastapi import Depends, HTTPException, status, WebSocket, Query
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from sqlalchemy.orm import Session
from sqlalchemy import create_engine
from app.core.config import settings
from app.models.user import User, Role

oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_STR}/auth/login")

# Database dependency
from app.db.session import SessionLocal

def get_db() -> Generator:
    # In tests, we override this dependency.
    if SessionLocal:
        db = SessionLocal()
        try:
            yield db
        finally:
            db.close()
    else:
        yield None

def get_current_user(
    db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)
) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        user_id: str = payload.get("sub")
        token_type: str = payload.get("type")
        if user_id is None or token_type != "access":
            raise credentials_exception
    except JWTError:
        raise credentials_exception
        
    user = db.query(User).filter(User.id == user_id, User.is_deleted == False).first()
    if user is None:
        raise credentials_exception
    return user

def get_current_active_user(
    current_user: User = Depends(get_current_user),
) -> User:
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user

class RoleChecker:
    def __init__(self, allowed_roles: List[str]):
        self.allowed_roles = allowed_roles

    def __call__(self, user: User = Depends(get_current_active_user), db: Session = Depends(get_db)):
        role = db.query(Role).filter(Role.id == user.role_id).first()
        if not role or role.name.upper() not in [r.upper() for r in self.allowed_roles]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Operation not permitted"
            )
        return user


async def get_ws_user(
    websocket: WebSocket,
    token: Optional[str] = Query(default=None),
    db: Session = Depends(get_db),
) -> Optional[User]:
    """
    WebSocket authentication via query parameter token.
    Usage: ws://host/ws/endpoint?token=<access_jwt>
    Closes the WebSocket with 4001 if authentication fails.
    Returns the authenticated User or None (caller must check).
    """
    if token is None:
        await websocket.close(code=4001, reason="Missing authentication token")
        return None
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        user_id: str = payload.get("sub")
        token_type: str = payload.get("type")
        if user_id is None or token_type != "access":
            await websocket.close(code=4001, reason="Invalid token")
            return None
    except JWTError:
        await websocket.close(code=4001, reason="Invalid token")
        return None

    if db is None:
        await websocket.close(code=4011, reason="Database unavailable")
        return None

    user = db.query(User).filter(User.id == user_id, User.is_deleted == False).first()
    if user is None or not user.is_active:
        await websocket.close(code=4001, reason="User not found or inactive")
        return None
    return user
