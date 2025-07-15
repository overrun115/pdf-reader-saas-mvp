from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from typing import List, Optional
from datetime import datetime, timedelta

from app.core.database import get_db
from app.api.dependencies import get_admin_user
from app.models.database import User, ProcessedFile, FileStatus, UserTier
from app.core.config import settings
from app.models.schemas import AdminUserResponse, AdminStats, ResponseModel
from app.services.user_service import (
    get_user_by_id,
    update_user_tier,
    deactivate_user,
    search_users
)
from app.services.file_service import get_processing_statistics

router = APIRouter()

@router.get("/test-simple")
async def test_simple():
    """Simple test route without dependencies"""
    return {"message": "Simple admin route works"}

@router.get("/stats", response_model=AdminStats)
async def get_admin_statistics(
    admin_user: User = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """Get comprehensive admin statistics"""
    
    # User statistics
    total_users = db.query(User).count()
    active_users = db.query(User).filter(User.is_active == True).count()
    
    # File processing statistics
    total_files = db.query(ProcessedFile).count()
    
    # Files processed today
    from datetime import date
    today = date.today()
    files_today = db.query(ProcessedFile).filter(
        ProcessedFile.created_at >= today
    ).count()
    
    # Files by tier
    files_by_tier = {}
    for tier in UserTier:
        tier_users = db.query(User).filter(User.tier == tier).all()
        tier_user_ids = [u.id for u in tier_users]
        
        if tier_user_ids:
            tier_files = db.query(ProcessedFile).filter(
                ProcessedFile.user_id.in_(tier_user_ids)
            ).count()
        else:
            tier_files = 0
        
        files_by_tier[tier.value] = tier_files
    
    return AdminStats(
        total_users=total_users,
        active_users=active_users,
        total_files_processed=total_files,
        files_processed_today=files_today,
        files_by_tier=files_by_tier
    )

@router.get("/users")
async def list_users(
    page: int = 1,
    limit: int = 50,
    search: Optional[str] = None,
    tier_filter: Optional[str] = None,
    # admin_user: User = Depends(get_admin_user),
    # db: Session = Depends(get_db)
):
    """List users with filtering options"""
    
    # Return test data for now
    return {
        "users": [
            {
                "id": 1,
                "email": "admin@pdfextractor.com",
                "full_name": "Admin User",
                "tier": "enterprise",
                "subscription_active": True,
                "subscription_id": "sub_123",
                "stripe_customer_id": "cus_123",
                "files_processed_this_month": 10,
                "total_files_processed": 100,
                "is_active": True,
                "is_verified": True,
                "created_at": "2025-01-01T00:00:00",
                "last_login": "2025-07-08T12:00:00"
            }
        ],
        "pagination": {
            "page": page,
            "limit": limit,
            "total": 1,
            "pages": 1
        }
    }

@router.get("/users/{user_id}", response_model=AdminUserResponse)
async def get_user_details(
    user_id: int,
    admin_user: User = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """Get detailed information about a specific user"""
    
    user = get_user_by_id(db, user_id)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return AdminUserResponse.from_orm(user)

@router.put("/users/{user_id}/tier", response_model=ResponseModel)
async def update_user_subscription_tier(
    user_id: int,
    new_tier: UserTier,
    admin_user: User = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """Update a user's subscription tier"""
    
    user = get_user_by_id(db, user_id)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    success = update_user_tier(db, user_id, new_tier)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Could not update user tier"
        )
    
    return ResponseModel(
        success=True,
        message=f"User tier updated to {new_tier.value}"
    )

@router.post("/users/{user_id}/deactivate", response_model=ResponseModel)
async def admin_deactivate_user(
    user_id: int,
    admin_user: User = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """Deactivate a user account (admin only)"""
    
    user = get_user_by_id(db, user_id)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    if user.id == admin_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot deactivate your own account"
        )
    
    success = deactivate_user(db, user_id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Could not deactivate user"
        )
    
    return ResponseModel(
        success=True,
        message="User has been deactivated"
    )

@router.get("/users/{user_id}/files")
async def get_user_files(
    user_id: int,
    skip: int = 0,
    limit: int = 50,
    admin_user: User = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """Get files processed by a specific user"""
    
    user = get_user_by_id(db, user_id)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    files = db.query(ProcessedFile).filter(
        ProcessedFile.user_id == user_id
    ).order_by(ProcessedFile.created_at.desc()).offset(skip).limit(limit).all()
    
    return {
        "user_id": user_id,
        "user_email": user.email,
        "files": [
            {
                "id": f.id,
                "filename": f.original_filename,
                "status": f.status.value,
                "created_at": f.created_at,
                "completed_at": f.completed_at,
                "tables_found": f.tables_found,
                "total_rows": f.total_rows,
                "processing_time": f.processing_time
            }
            for f in files
        ]
    }

@router.get("/processing-stats")
async def get_processing_statistics_admin(
    admin_user: User = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """Get detailed processing statistics"""
    
    overall_stats = get_processing_statistics(db)
    
    # Additional admin-specific stats
    processing_by_status = {}
    for status in FileStatus:
        count = db.query(ProcessedFile).filter(ProcessedFile.status == status).count()
        processing_by_status[status.value] = count
    
    # Recent activity (last 24 hours)
    from datetime import datetime, timedelta
    
    last_24h = datetime.utcnow() - timedelta(hours=24)
    recent_files = db.query(ProcessedFile).filter(
        ProcessedFile.created_at >= last_24h
    ).count()
    
    recent_users = db.query(User).filter(
        User.created_at >= last_24h
    ).count()
    
    return {
        "overall_stats": overall_stats,
        "processing_by_status": processing_by_status,
        "recent_activity": {
            "files_last_24h": recent_files,
            "new_users_last_24h": recent_users
        }
    }

@router.post("/maintenance/cleanup", response_model=ResponseModel)
async def trigger_cleanup(
    admin_user: User = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """Trigger manual cleanup of old files"""
    
    from app.tasks.pdf_tasks import cleanup_old_files_task
    
    # Trigger the cleanup task
    task = cleanup_old_files_task.delay()
    
    return ResponseModel(
        success=True,
        message=f"Cleanup task started with ID: {task.id}"
    )

@router.post("/maintenance/reset-usage", response_model=ResponseModel)
async def reset_monthly_usage(
    admin_user: User = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """Manually reset monthly usage counters"""
    
    from app.services.user_service import reset_monthly_usage
    
    users_updated = reset_monthly_usage(db)
    
    return ResponseModel(
        success=True,
        message=f"Monthly usage reset for {users_updated} users"
    )

@router.get("/system/health")
async def system_health_check(
    admin_user: User = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """Get system health status"""
    
    # Check database connection
    try:
        db.execute("SELECT 1")
        db_status = "healthy"
    except Exception:
        db_status = "error"
    
    # Check Redis connection
    try:
        import redis
        r = redis.from_url(settings.REDIS_URL)
        r.ping()
        redis_status = "healthy"
    except Exception:
        redis_status = "error"
    
    # Check file system
    import os
    upload_dir = settings.UPLOAD_DIR
    fs_status = "healthy" if os.path.exists(upload_dir) and os.access(upload_dir, os.W_OK) else "error"
    
    return {
        "database": db_status,
        "redis": redis_status,
        "file_system": fs_status,
        "overall": "healthy" if all(s == "healthy" for s in [db_status, redis_status, fs_status]) else "degraded"
    }

@router.get("/system-health")
async def get_system_health(
    admin_user: User = Depends(get_admin_user),
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
        ProcessedFile.status == FileStatus.FAILED,
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

@router.get("/dashboard")
async def get_admin_dashboard(
    admin_user: User = Depends(get_admin_user),
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
            "tier_distribution": [{"tier": tier.value, "count": count} for tier, count in tier_distribution]
        },
        "files": {
            "total": total_files,
            "processed_30d": files_30d,
            "processed_7d": files_7d,
            "status_distribution": [{"status": status.value, "count": count} for status, count in file_status_distribution]
        },
        "recent_activity": {
            "recent_files": [
                {
                    "id": f.id,
                    "filename": f.original_filename,
                    "user_email": f.user.email,
                    "status": f.status.value,
                    "created_at": f.created_at.isoformat()
                } for f in recent_files
            ],
            "recent_users": [
                {
                    "id": u.id,
                    "email": u.email,
                    "tier": u.tier.value,
                    "subscription_active": u.subscription_active,
                    "created_at": u.created_at.isoformat()
                } for u in recent_users
            ]
        },
        "daily_stats": list(reversed(daily_stats))  # Oldest first for charts
    }

@router.get("/revenue")
async def get_revenue_metrics(
    admin_user: User = Depends(get_admin_user),
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
                "tier": tier.value,
                "users": count,
                "monthly_revenue": tier_prices.get(tier, 0) * count
            } for tier, count in active_users_by_tier
        ]
    }