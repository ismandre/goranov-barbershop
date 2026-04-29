"""Authentication endpoints."""

from datetime import timedelta
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.database import get_db_session
from app.database.models import Admin
from app.auth import create_access_token, verify_password, get_current_admin
from app.config import JWT_EXPIRATION_HOURS


router = APIRouter(prefix="/admin/auth", tags=["Authentication"])


class LoginRequest(BaseModel):
    """Login request body."""
    username: str
    password: str


class LoginResponse(BaseModel):
    """Login response with JWT token."""
    access_token: str
    token_type: str = "bearer"
    expires_in: int  # seconds
    admin_id: int
    username: str


class AdminInfo(BaseModel):
    """Admin user information."""
    id: int
    username: str
    phone_number: Optional[str]
    created_at: str


@router.post("/login", response_model=LoginResponse)
def login(
    credentials: LoginRequest,
    db: Session = Depends(get_db_session)
):
    """
    Admin login endpoint.

    Authenticates admin credentials and returns JWT access token.

    **Request:**
    ```json
    {
        "username": "barber",
        "password": "your-password"
    }
    ```

    **Response:**
    ```json
    {
        "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
        "token_type": "bearer",
        "expires_in": 86400,
        "admin_id": 1,
        "username": "barber"
    }
    ```

    **Usage:**
    Include the token in subsequent requests:
    ```
    Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGc...
    ```
    """
    # Find admin by username
    admin = db.query(Admin).filter(Admin.username == credentials.username).first()

    if not admin:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Verify password
    if not verify_password(credentials.password, admin.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Create access token
    access_token_expires = timedelta(hours=JWT_EXPIRATION_HOURS)
    access_token = create_access_token(
        data={"sub": admin.username},
        expires_delta=access_token_expires
    )

    return LoginResponse(
        access_token=access_token,
        token_type="bearer",
        expires_in=int(access_token_expires.total_seconds()),
        admin_id=admin.id,
        username=admin.username
    )


@router.get("/me", response_model=AdminInfo)
def get_current_admin_info(
    admin: Admin = Depends(get_current_admin)
):
    """
    Get current authenticated admin information.

    Requires authentication (Bearer token).

    **Response:**
    ```json
    {
        "id": 1,
        "username": "barber",
        "phone_number": "+385123456789",
        "created_at": "2024-12-05T10:30:00"
    }
    ```
    """
    return AdminInfo(
        id=admin.id,
        username=admin.username,
        phone_number=admin.phone_number,
        created_at=admin.created_at.isoformat()
    )


@router.post("/verify")
def verify_token_endpoint(
    admin: Admin = Depends(get_current_admin)
):
    """
    Verify if the provided token is valid.

    Requires authentication (Bearer token).

    **Response:**
    ```json
    {
        "valid": true,
        "username": "barber",
        "admin_id": 1
    }
    ```
    """
    return {
        "valid": True,
        "username": admin.username,
        "admin_id": admin.id
    }
