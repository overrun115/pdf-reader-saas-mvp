from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.api.dependencies import get_current_active_user
from app.models.database import User
from app.models.schemas import UserResponse, UserUpdate, ResponseModel
from pydantic import BaseModel
from app.services.user_service import (
    update_user_profile, 
    get_user_usage_stats,
    get_user_by_id
)

router = APIRouter()

# Pydantic models for requests
class ChangePasswordRequest(BaseModel):
    current_password: str
    new_password: str

class ProfileUpdateRequest(BaseModel):
    full_name: str
    email: str

@router.get("/me", response_model=UserResponse)
async def get_current_user_profile(
    current_user: User = Depends(get_current_active_user)
):
    """Get current user's profile information"""
    return current_user

@router.put("/me", response_model=UserResponse)
async def update_current_user_profile(
    user_update: UserUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Update current user's profile"""
    
    updated_user = update_user_profile(
        db=db,
        user_id=current_user.id,
        full_name=user_update.full_name,
        email=user_update.email
    )
    
    if not updated_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Could not update profile. Email may already be in use."
        )
    
    return updated_user

@router.put("/profile", response_model=UserResponse)
async def update_user_profile_endpoint(
    profile_update: ProfileUpdateRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Update current user's profile (alternative endpoint)"""
    
    # Check if email is already in use by another user
    if profile_update.email != current_user.email:
        existing_user = db.query(User).filter(
            User.email == profile_update.email,
            User.id != current_user.id
        ).first()
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already in use"
            )
    
    # Update user fields
    current_user.full_name = profile_update.full_name
    current_user.email = profile_update.email
    
    db.commit()
    db.refresh(current_user)
    
    return current_user

@router.put("/change-password")
async def change_password(
    password_request: ChangePasswordRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Change user's password"""
    from app.core.security import verify_password, get_password_hash
    
    # Verify current password
    if not verify_password(password_request.current_password, current_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Current password is incorrect"
        )
    
    # Hash new password
    new_hashed_password = get_password_hash(password_request.new_password)
    
    # Update password
    current_user.hashed_password = new_hashed_password
    db.commit()
    
    return {"message": "Password changed successfully"}

@router.get("/me/usage", response_model=dict)
async def get_user_usage(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get current user's usage statistics"""
    
    usage_stats = get_user_usage_stats(db, current_user.id)
    
    return {
        "success": True,
        "data": usage_stats
    }

@router.get("/me/subscription", response_model=dict)
async def get_user_subscription(
    current_user: User = Depends(get_current_active_user)
):
    """Get current user's subscription information"""
    
    # Calculate tier features
    tier_features = {
        "free": {
            "monthly_limit": 5,
            "formats": ["excel"],
            "api_access": False,
            "priority_processing": False,
            "email_support": False
        },
        "basic": {
            "monthly_limit": 50,
            "formats": ["excel", "csv", "both"],
            "api_access": False,
            "priority_processing": False,
            "email_support": True
        },
        "pro": {
            "monthly_limit": 200,
            "formats": ["excel", "csv", "both"],
            "api_access": True,
            "priority_processing": True,
            "email_support": True
        },
        "enterprise": {
            "monthly_limit": -1,  # Unlimited
            "formats": ["excel", "csv", "both"],
            "api_access": True,
            "priority_processing": True,
            "email_support": True,
            "custom_integrations": True,
            "sla_guarantee": True
        }
    }
    
    current_features = tier_features.get(current_user.tier.value, tier_features["free"])
    
    return {
        "success": True,
        "data": {
            "tier": current_user.tier.value,
            "subscription_active": current_user.subscription_active,
            "subscription_id": current_user.subscription_id,
            "features": current_features,
            "usage": {
                "files_processed_this_month": current_user.files_processed_this_month,
                "monthly_limit": current_features["monthly_limit"],
                "remaining": max(0, current_features["monthly_limit"] - current_user.files_processed_this_month) if current_features["monthly_limit"] != -1 else -1
            }
        }
    }

@router.post("/me/deactivate", response_model=ResponseModel)
async def deactivate_account(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Deactivate current user's account"""
    
    from app.services.user_service import deactivate_user
    
    success = deactivate_user(db, current_user.id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Could not deactivate account"
        )
    
    return ResponseModel(
        success=True,
        message="Account has been deactivated successfully"
    )

@router.get("/me/api-keys", response_model=dict)
async def get_user_api_keys(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get current user's API keys"""
    
    # Check if user has API access
    if current_user.tier.value not in ["pro", "enterprise"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="API access not available for your subscription tier"
        )
    
    from app.models.database import APIKey
    
    api_keys = db.query(APIKey).filter(
        APIKey.user_id == current_user.id,
        APIKey.is_active == True
    ).all()
    
    keys_data = []
    for key in api_keys:
        keys_data.append({
            "id": key.id,
            "name": key.key_name,
            "prefix": key.key_prefix,
            "requests_made": key.requests_made,
            "last_used": key.last_used,
            "created_at": key.created_at,
            "expires_at": key.expires_at
        })
    
    return {
        "success": True,
        "data": {
            "api_keys": keys_data,
            "max_keys": 5 if current_user.tier.value == "pro" else 10  # Enterprise gets more
        }
    }

@router.post("/me/api-keys", response_model=dict)
async def create_api_key(
    key_name: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Create a new API key for the user"""
    
    # Check if user has API access
    if current_user.tier.value not in ["pro", "enterprise"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="API access not available for your subscription tier"
        )
    
    # Check key limit
    from app.models.database import APIKey
    
    existing_keys = db.query(APIKey).filter(
        APIKey.user_id == current_user.id,
        APIKey.is_active == True
    ).count()
    
    max_keys = 5 if current_user.tier.value == "pro" else 10
    
    if existing_keys >= max_keys:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Maximum number of API keys ({max_keys}) reached"
        )
    
    # Generate API key
    import secrets
    import hashlib
    
    api_key = secrets.token_urlsafe(32)
    key_hash = hashlib.sha256(api_key.encode()).hexdigest()
    key_prefix = api_key[:8]
    
    # Save to database
    db_api_key = APIKey(
        user_id=current_user.id,
        key_name=key_name,
        key_hash=key_hash,
        key_prefix=key_prefix,
        is_active=True
    )
    
    db.add(db_api_key)
    db.commit()
    db.refresh(db_api_key)
    
    return {
        "success": True,
        "data": {
            "id": db_api_key.id,
            "name": key_name,
            "api_key": api_key,  # Only returned once
            "prefix": key_prefix,
            "created_at": db_api_key.created_at
        },
        "message": "API key created successfully. Save it securely - it won't be shown again."
    }

@router.delete("/me/api-keys/{key_id}", response_model=ResponseModel)
async def delete_api_key(
    key_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Delete an API key"""
    
    from app.models.database import APIKey
    
    api_key = db.query(APIKey).filter(
        APIKey.id == key_id,
        APIKey.user_id == current_user.id
    ).first()
    
    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="API key not found"
        )
    
    api_key.is_active = False
    db.commit()
    
    return ResponseModel(
        success=True,
        message="API key has been deactivated"
    )