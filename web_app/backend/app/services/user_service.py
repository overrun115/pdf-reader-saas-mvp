from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime

from app.models.database import User, UserTier
from app.models.schemas import UserCreate
from app.core.security import get_password_hash, verify_password

def get_user_by_email(db: Session, email: str) -> Optional[User]:
    """Get user by email address"""
    return db.query(User).filter(User.email == email).first()

def get_user_by_id(db: Session, user_id: int) -> Optional[User]:
    """Get user by ID"""
    return db.query(User).filter(User.id == user_id).first()

def create_user(db: Session, user: UserCreate) -> User:
    """Create a new user"""
    
    hashed_password = get_password_hash(user.password)
    
    db_user = User(
        email=user.email,
        full_name=user.full_name,
        hashed_password=hashed_password,
        tier=UserTier.FREE,
        is_active=True,
        is_verified=False  # Email verification required
    )
    
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    return db_user

def authenticate_user(db: Session, email: str, password: str) -> Optional[User]:
    """Authenticate user with email and password"""
    
    user = get_user_by_email(db, email)
    
    if not user:
        return None
    
    if not verify_password(password, user.hashed_password):
        return None
    
    return user

def update_user_last_login(db: Session, user_id: int) -> bool:
    """Update user's last login timestamp"""
    
    user = get_user_by_id(db, user_id)
    
    if not user:
        return False
    
    user.last_login = datetime.utcnow()
    db.commit()
    
    return True

def update_user_password(db: Session, user_id: int, new_password: str) -> bool:
    """Update user's password"""
    
    user = get_user_by_id(db, user_id)
    
    if not user:
        return False
    
    user.hashed_password = get_password_hash(new_password)
    db.commit()
    
    return True

def update_user_profile(db: Session, user_id: int, full_name: Optional[str] = None, email: Optional[str] = None) -> Optional[User]:
    """Update user profile information"""
    
    user = get_user_by_id(db, user_id)
    
    if not user:
        return None
    
    if full_name is not None:
        user.full_name = full_name
    
    if email is not None:
        # Check if email is already taken
        existing_user = get_user_by_email(db, email)
        if existing_user and existing_user.id != user_id:
            return None  # Email already taken
        
        user.email = email
        user.is_verified = False  # Require re-verification
    
    db.commit()
    db.refresh(user)
    
    return user

def update_user_tier(db: Session, user_id: int, new_tier: UserTier, subscription_id: Optional[str] = None) -> bool:
    """Update user's subscription tier"""
    
    user = get_user_by_id(db, user_id)
    
    if not user:
        return False
    
    user.tier = new_tier
    user.subscription_active = True
    
    if subscription_id:
        user.subscription_id = subscription_id
    
    db.commit()
    
    return True

def deactivate_user(db: Session, user_id: int) -> bool:
    """Deactivate a user account"""
    
    user = get_user_by_id(db, user_id)
    
    if not user:
        return False
    
    user.is_active = False
    user.subscription_active = False
    db.commit()
    
    return True

def verify_user_email(db: Session, user_id: int) -> bool:
    """Mark user's email as verified"""
    
    user = get_user_by_id(db, user_id)
    
    if not user:
        return False
    
    user.is_verified = True
    db.commit()
    
    return True

def reset_monthly_usage(db: Session, user_id: Optional[int] = None) -> int:
    """Reset monthly file processing count for users"""
    
    query = db.query(User)
    
    if user_id:
        query = query.filter(User.id == user_id)
    
    users_updated = query.update({"files_processed_this_month": 0})
    db.commit()
    
    return users_updated

def get_user_usage_stats(db: Session, user_id: int) -> dict:
    """Get detailed usage statistics for a user"""
    
    user = get_user_by_id(db, user_id)
    
    if not user:
        return {}
    
    # Calculate tier limits
    tier_limits = {
        UserTier.FREE: 5,
        UserTier.BASIC: 50,
        UserTier.PRO: 200,
        UserTier.ENTERPRISE: -1  # Unlimited
    }
    
    tier_limit = tier_limits.get(user.tier, 5)
    remaining = max(0, tier_limit - user.files_processed_this_month) if tier_limit != -1 else -1
    
    usage_percentage = (user.files_processed_this_month / tier_limit * 100) if tier_limit > 0 else 0
    
    return {
        "user_tier": user.tier.value,
        "files_processed_this_month": user.files_processed_this_month,
        "total_files_processed": user.total_files_processed,
        "tier_limit": tier_limit,
        "remaining_files": remaining,
        "usage_percentage": usage_percentage,
        "subscription_active": user.subscription_active,
        "account_created": user.created_at,
        "last_login": user.last_login
    }

def get_users_by_tier(db: Session, tier: UserTier) -> list[User]:
    """Get all users by subscription tier"""
    
    return db.query(User).filter(User.tier == tier).all()

def search_users(db: Session, query: str, limit: int = 50) -> list[User]:
    """Search users by email or name"""
    
    search_pattern = f"%{query}%"
    
    return db.query(User).filter(
        (User.email.ilike(search_pattern)) |
        (User.full_name.ilike(search_pattern))
    ).limit(limit).all()