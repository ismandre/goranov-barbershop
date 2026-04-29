"""FastAPI dependencies for authentication."""

from typing import Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from app.database import get_db_session
from app.database.models import Admin
from app.auth.jwt_handler import verify_token


# HTTP Bearer token scheme
security = HTTPBearer()


def get_current_admin(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db_session)
) -> Admin:
    """
    Dependency to get current authenticated admin.

    Validates JWT token and returns the admin user.
    Raises 401 if token is invalid or admin not found.

    Usage:
        @app.get("/admin/protected")
        def protected_route(admin: Admin = Depends(get_current_admin)):
            return {"username": admin.username}
    """
    token = credentials.credentials

    # Verify token
    payload = verify_token(token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Get username from token
    username: Optional[str] = payload.get("sub")
    if not username:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Get admin from database
    admin = db.query(Admin).filter(Admin.username == username).first()
    if not admin:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Admin user not found",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return admin


def get_current_admin_optional(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(HTTPBearer(auto_error=False)),
    db: Session = Depends(get_db_session)
) -> Optional[Admin]:
    """
    Optional authentication dependency.
    Returns admin if authenticated, None if not.
    Does not raise exception if no token provided.
    """
    if not credentials:
        return None

    try:
        return get_current_admin(credentials, db)
    except HTTPException:
        return None
