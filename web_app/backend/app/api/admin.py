from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, extract, desc
from app.core.database import get_db
from app.api.dependencies import get_current_user
from app.models.database import User, ProcessedFile, UserTier
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)
router = APIRouter(tags=["admin"])

def is_admin(current_user: User = Depends(get_current_user)) -> User:
    """Check if user is admin"""
    if current_user.email != "admin@pdfextractor.com":  # Simple admin check
        raise HTTPException(status_code=403, detail="Admin access required")
    return current_user

@router.get("/dashboard")
async def get_admin_dashboard(
    admin_user: User = Depends(is_admin),
    db: Session = Depends(get_db)
):
    """Get comprehensive admin dashboard data"""
    
    # Date ranges
    now = datetime.utcnow()
    thirty_days_ago = now - timedelta(days=30)
    seven_days_ago = now - timedelta(days=7)
    
    # User metrics
    total_users = db.query(User).count()
    new_users_30d = db.query(User).filter(User.created_at >= thirty_days_ago).count()
    new_users_7d = db.query(User).filter(User.created_at >= seven_days_ago).count()
    
    # Subscription metrics
    active_subscriptions = db.query(User).filter(User.subscription_active == True).count()
    
    # Tier distribution
    tier_distribution = db.query(
        User.tier, 
        func.count(User.id).label('count')
    ).group_by(User.tier).all()
    
    # File processing metrics
    total_files = db.query(ProcessedFile).count()
    files_30d = db.query(ProcessedFile).filter(ProcessedFile.created_at >= thirty_days_ago).count()
    files_7d = db.query(ProcessedFile).filter(ProcessedFile.created_at >= seven_days_ago).count()
    
    # File status distribution
    file_status_distribution = db.query(
        ProcessedFile.status,
        func.count(ProcessedFile.id).label('count')
    ).group_by(ProcessedFile.status).all()
    
    # Recent activity
    recent_files = db.query(ProcessedFile).order_by(desc(ProcessedFile.created_at)).limit(10).all()
    recent_users = db.query(User).order_by(desc(User.created_at)).limit(10).all()
    
    # Daily statistics for charts (last 30 days)
    daily_stats = []
    for i in range(30):
        date = now - timedelta(days=i)
        day_start = date.replace(hour=0, minute=0, second=0, microsecond=0)
        day_end = day_start + timedelta(days=1)
        
        users_count = db.query(User).filter(
            User.created_at >= day_start,
            User.created_at < day_end
        ).count()
        
        files_count = db.query(ProcessedFile).filter(
            ProcessedFile.created_at >= day_start,
            ProcessedFile.created_at < day_end
        ).count()
        
        daily_stats.append({
            "date": day_start.isoformat(),
            "new_users": users_count,
            "files_processed": files_count
        })
    
    return {
        "users": {
            "total": total_users,
            "new_30d": new_users_30d,
            "new_7d": new_users_7d,
            "active_subscriptions": active_subscriptions,
            "tier_distribution": [{"tier": tier, "count": count} for tier, count in tier_distribution]
        },
        "files": {
            "total": total_files,
            "processed_30d": files_30d,
            "processed_7d": files_7d,
            "status_distribution": [{"status": status, "count": count} for status, count in file_status_distribution]
        },
        "recent_activity": {
            "recent_files": [
                {
                    "id": f.id,
                    "filename": f.original_filename,
                    "user_email": f.user.email,
                    "status": f.status,
                    "created_at": f.created_at.isoformat()
                } for f in recent_files
            ],
            "recent_users": [
                {
                    "id": u.id,
                    "email": u.email,
                    "tier": u.tier,
                    "subscription_active": u.subscription_active,
                    "created_at": u.created_at.isoformat()
                } for u in recent_users
            ]
        },
        "daily_stats": list(reversed(daily_stats))  # Oldest first for charts
    }

@router.get("/users")
async def get_users_list(
    admin_user: User = Depends(is_admin),
    db: Session = Depends(get_db),
    page: int = Query(1, ge=1),
    limit: int = Query(50, ge=1, le=100),
    search: Optional[str] = Query(None),
    tier_filter: Optional[str] = Query(None)
):
    """Get paginated list of users with filters"""
    
    query = db.query(User)
    
    # Apply filters
    if search:
        query = query.filter(User.email.ilike(f"%{search}%"))
    
    if tier_filter:
        query = query.filter(User.tier == tier_filter)
    
    # Get total count
    total = query.count()
    
    # Apply pagination
    offset = (page - 1) * limit
    users = query.order_by(desc(User.created_at)).offset(offset).limit(limit).all()
    
    return {
        "users": [
            {
                "id": u.id,
                "email": u.email,
                "full_name": u.full_name,
                "tier": u.tier,
                "subscription_active": u.subscription_active,
                "subscription_id": u.subscription_id,
                "stripe_customer_id": u.stripe_customer_id,
                "files_processed_this_month": u.files_processed_this_month,
                "total_files_processed": u.total_files_processed,
                "is_active": u.is_active,
                "is_verified": u.is_verified,
                "created_at": u.created_at.isoformat(),
                "last_login": u.last_login.isoformat() if u.last_login else None
            } for u in users
        ],
        "pagination": {
            "page": page,
            "limit": limit,
            "total": total,
            "pages": (total + limit - 1) // limit
        }
    }

@router.put("/users/{user_id}/tier")
async def update_user_tier(
    user_id: int,
    tier: UserTier,
    admin_user: User = Depends(is_admin),
    db: Session = Depends(get_db)
):
    """Update user tier manually"""
    
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    old_tier = user.tier
    user.tier = tier
    db.commit()
    
    logger.info(f"Admin {admin_user.email} changed user {user.email} tier from {old_tier} to {tier}")
    
    return {"message": f"User tier updated from {old_tier} to {tier}"}

@router.get("/revenue")
async def get_revenue_metrics(
    admin_user: User = Depends(is_admin),
    db: Session = Depends(get_db)
):
    """Get revenue and subscription metrics"""
    
    # Basic tier pricing (should match your Stripe configuration)
    tier_prices = {
        UserTier.FREE: 0,
        UserTier.BASIC: 9.99,
        UserTier.PRO: 29.99,
        UserTier.ENTERPRISE: 99.99
    }
    
    # Current MRR calculation
    active_users_by_tier = db.query(
        User.tier,
        func.count(User.id).label('count')
    ).filter(User.subscription_active == True).group_by(User.tier).all()
    
    mrr = sum(tier_prices.get(tier, 0) * count for tier, count in active_users_by_tier)
    arr = mrr * 12
    
    # Growth metrics
    now = datetime.utcnow()
    last_month = now - timedelta(days=30)
    
    new_subscriptions_30d = db.query(User).filter(
        User.subscription_active == True,
        User.created_at >= last_month
    ).count()
    
    return {
        "mrr": round(mrr, 2),
        "arr": round(arr, 2),
        "active_subscriptions": sum(count for _, count in active_users_by_tier),
        "new_subscriptions_30d": new_subscriptions_30d,
        "tier_revenue": [
            {
                "tier": tier,
                "users": count,
                "monthly_revenue": tier_prices.get(tier, 0) * count
            } for tier, count in active_users_by_tier
        ]
    }

@router.get("/system-health")
async def get_system_health(
    admin_user: User = Depends(is_admin),
    db: Session = Depends(get_db)
):
    """Get system health metrics"""
    
    # Database connection test
    try:
        db.execute("SELECT 1")
        db_status = "healthy"
    except Exception as e:
        db_status = f"error: {str(e)}"
    
    # Recent error count (simplified - you'd want to track this properly)
    recent_failed_files = db.query(ProcessedFile).filter(
        ProcessedFile.status == "failed",
        ProcessedFile.created_at >= datetime.utcnow() - timedelta(hours=24)
    ).count()
    
    return {
        "database": {
            "status": db_status,
            "total_tables": ["users", "processed_files", "api_keys", "usage_logs"]
        },
        "processing": {
            "failed_files_24h": recent_failed_files,
            "queue_status": "active"  # You'd check Celery queue here
        },
        "uptime": "Running"  # You'd calculate actual uptime
    }