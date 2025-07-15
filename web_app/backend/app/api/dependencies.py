from fastapi import Depends, HTTPException, status, UploadFile
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from typing import Optional
# import magic  # Temporarily disabled - requires libmagic installation

from app.core.database import get_db
from app.core.security import verify_token
from app.core.config import settings
from app.models.database import User
from app.services.user_service import get_user_by_email

# Security scheme
security = HTTPBearer()

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """Get current authenticated user"""
    token = credentials.credentials
    
    try:
        payload = verify_token(token)
        email = payload.get("sub")
        if email is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials"
            )
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials"
        )
    
    user = get_user_by_email(db, email)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )
    
    return user

async def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """Get current active user"""
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )
    return current_user

async def get_admin_user(
    current_user: User = Depends(get_current_active_user)
) -> User:
    """Get current user and verify admin privileges"""
    # For now, we'll use email-based admin check
    # In production, you'd want a proper role system
    admin_emails = ["admin@pdfextractor.com"]  # Configure in settings
    
    if current_user.email not in admin_emails:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    return current_user

async def validate_file_upload(file: UploadFile) -> UploadFile:
    """Validate uploaded file"""
    
    # Check file size
    if file.size and file.size > settings.MAX_FILE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"File too large. Maximum size is {settings.MAX_FILE_SIZE / 1024 / 1024:.1f}MB"
        )
    
    # Check file type
    if file.content_type not in settings.ALLOWED_FILE_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid file type. Only PDF files are allowed"
        )
    
    # Basic validation - check file extension
    if not file.filename or not file.filename.lower().endswith('.pdf'):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid file extension. Only PDF files are allowed"
        )
    
    return file

def check_user_limits(user: User) -> bool:
    """Check if user has reached their processing limits"""
    limits = {
        "free": settings.FREE_TIER_LIMIT,
        "basic": settings.BASIC_TIER_LIMIT,
        "pro": settings.PRO_TIER_LIMIT,
        "enterprise": settings.ENTERPRISE_TIER_LIMIT
    }
    
    user_limit = limits.get(user.tier.value, settings.FREE_TIER_LIMIT)
    
    # Unlimited for enterprise
    if user_limit == -1:
        return True
    
    return user.files_processed_this_month < user_limit

async def require_processing_quota(
    current_user: User = Depends(get_current_active_user)
) -> User:
    """Ensure user has processing quota available"""
    if not check_user_limits(current_user):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Monthly processing limit reached. Please upgrade your plan."
        )
    
    return current_user