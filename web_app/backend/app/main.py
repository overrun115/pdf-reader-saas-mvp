from fastapi import FastAPI, Depends, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from typing import Optional
import os
import sys
import logging
from datetime import datetime

# Add paths for shared modules
sys.path.append(os.path.join(os.path.dirname(__file__), "../../../"))
sys.path.append(os.path.join(os.path.dirname(__file__), "../../"))

# Core imports
from app.core.database import get_db, engine
from app.core.config import settings
from app.models import database
from app.api.dependencies import get_current_active_user

# Route imports
from app.api.routes import auth, users, trial, contact, pdf_viewer, email_verification, files
from app.api import subscription, webhooks

# Create database tables
database.Base.metadata.create_all(bind=engine)

# Initialize FastAPI app
app = FastAPI(
    title="PDF Table Extractor API",
    description="SaaS API for extracting tables from PDF files", 
    version="1.0.0",
    docs_url="/docs" if settings.ENVIRONMENT == "development" else None,
    redoc_url="/redoc" if settings.ENVIRONMENT == "development" else None,
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# Configure logging
logging.basicConfig(
    level=logging.INFO if not settings.DEBUG else logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Handle unexpected errors gracefully"""
    if settings.DEBUG:
        # In development, show detailed error
        logger.exception(f"Unexpected error: {exc}")
        return JSONResponse(
            status_code=500,
            content={
                "error": "Internal server error",
                "detail": str(exc),
                "type": type(exc).__name__
            }
        )
    else:
        # In production, hide error details
        logger.error(f"Internal server error: {exc}")
        return JSONResponse(
            status_code=500,
            content={"error": "Internal server error"}
        )

# Health check endpoint
@app.get("/api/health")
async def health_check():
    return {
        "status": "ok", 
        "message": "Backend is running",
        "timestamp": datetime.now().isoformat(),
        "environment": settings.ENVIRONMENT,
        "version": settings.VERSION
    }

@app.get("/api/test-working")
async def test_working():
    return {"status": "success", "message": "New main.py is working", "timestamp": "2025-07-08-21:51"}

@app.get("/api/cors-test")
async def cors_test():
    """Test endpoint to verify CORS is working"""
    return {
        "status": "success",
        "message": "CORS is working correctly",
        "cors_enabled": True
    }

# Include routers
app.include_router(auth.router, prefix="/api/auth", tags=["authentication"])
app.include_router(users.router, prefix="/api/users", tags=["users"])
app.include_router(files.router, prefix="/api/files", tags=["files"])
app.include_router(trial.router, prefix="/api", tags=["trial"])
app.include_router(contact.router, prefix="/api", tags=["contact"])
app.include_router(pdf_viewer.router, prefix="/api", tags=["pdf-viewer"])
app.include_router(subscription.router, prefix="/api", tags=["subscription"])
app.include_router(webhooks.router, prefix="/api", tags=["webhooks"])
app.include_router(email_verification.router, prefix="/api/email", tags=["email-verification"])

# Admin functionality - direct implementation with different prefix to avoid blocking
def get_admin_user(current_user = Depends(get_current_active_user)):
    """Check if user is admin"""
    admin_emails = ["admin@pdfextractor.com", "admin@test.com", "admin@duehub.app"]
    admin_ids = [1, 2]  # IDs of admin users
    
    is_admin = (current_user.email in admin_emails or 
                current_user.id in admin_ids or
                current_user.tier.value == "ENTERPRISE")  # Enterprise users can be admins
    
    if not is_admin:
        raise HTTPException(status_code=403, detail="Admin access required")
    return current_user

@app.get("/api/management/users")
async def admin_list_users(
    page: int = 1,
    limit: int = 50,
    search: Optional[str] = None,
    tier_filter: Optional[str] = None,
    admin_user = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """List users with filtering options"""
    from app.models.database import User
    from datetime import datetime, timedelta
    from sqlalchemy import desc
    
    query = db.query(User)
    
    # Apply search filter
    if search:
        query = query.filter(User.email.ilike(f"%{search}%"))
    
    # Apply tier filter
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
                "tier": u.tier.value if hasattr(u.tier, 'value') else str(u.tier),
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

@app.post("/api/management/users")
async def admin_create_user(
    user_data: dict,
    admin_user = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """Create a new user"""
    from app.models.database import User, UserTier
    from app.core.security import get_password_hash
    from datetime import datetime
    
    # Check if user already exists
    existing_user = db.query(User).filter(User.email == user_data["email"]).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="User with this email already exists")
    
    # Create new user
    hashed_password = get_password_hash(user_data["password"])
    
    new_user = User(
        email=user_data["email"],
        full_name=user_data["full_name"],
        hashed_password=hashed_password,
        tier=UserTier(user_data["tier"]),
        subscription_active=True,
        is_active=True,
        is_verified=True,
        created_at=datetime.utcnow(),
        last_login=datetime.utcnow()
    )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    return {
        "message": "User created successfully",
        "user": {
            "id": new_user.id,
            "email": new_user.email,
            "full_name": new_user.full_name,
            "tier": new_user.tier.value,
            "subscription_active": new_user.subscription_active,
            "is_active": new_user.is_active,
            "is_verified": new_user.is_verified,
            "created_at": new_user.created_at.isoformat()
        }
    }

@app.put("/api/management/users/{user_id}/tier")
async def admin_update_user_tier(
    user_id: int,
    tier_data: dict,
    admin_user = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """Update user tier"""
    from app.models.database import User, UserTier
    
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    user.tier = UserTier(tier_data["tier"])
    db.commit()
    
    return {"message": "User tier updated successfully"}

@app.put("/api/management/users/{user_id}/status")
async def admin_update_user_status(
    user_id: int,
    status_data: dict,
    admin_user = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """Update user active status"""
    from app.models.database import User
    
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    user.is_active = status_data["is_active"]
    db.commit()
    
    return {"message": "User status updated successfully"}

@app.put("/api/management/users/{user_id}/subscription")
async def admin_update_user_subscription(
    user_id: int,
    subscription_data: dict,
    admin_user = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """Update user subscription status"""
    from app.models.database import User
    
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    user.subscription_active = subscription_data["subscription_active"]
    db.commit()
    
    return {"message": "User subscription updated successfully"}

@app.delete("/api/management/users/{user_id}")
async def admin_delete_user(
    user_id: int,
    admin_user = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """Delete a user and all associated data"""
    from app.models.database import User, ProcessedFile, APIKey, UsageLog
    
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Don't allow deleting admin users
    admin_emails = ["admin@pdfextractor.com", "admin@test.com", "admin@duehub.app"]
    if user.email in admin_emails:
        raise HTTPException(status_code=403, detail="Cannot delete admin user")
    
    try:
        # Delete related records first (in order of dependencies)
        # Delete processed files
        db.query(ProcessedFile).filter(ProcessedFile.user_id == user_id).delete()
        
        # Delete API keys
        db.query(APIKey).filter(APIKey.user_id == user_id).delete()
        
        # Delete usage logs
        db.query(UsageLog).filter(UsageLog.user_id == user_id).delete()
        
        # Finally delete the user
        db.delete(user)
        db.commit()
        
        return {"message": "User and all associated data deleted successfully"}
    
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error deleting user: {str(e)}")

@app.get("/api/management/dashboard")
async def admin_dashboard(
    admin_user = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """Get comprehensive admin dashboard data - real data only"""
    from app.models.database import User, ProcessedFile
    from datetime import datetime, timedelta
    from sqlalchemy import func, desc
    
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
    
    # File processing metrics
    total_files = db.query(ProcessedFile).count()
    files_30d = db.query(ProcessedFile).filter(ProcessedFile.created_at >= thirty_days_ago).count()
    files_7d = db.query(ProcessedFile).filter(ProcessedFile.created_at >= seven_days_ago).count()
    
    # Get recent files
    recent_files = db.query(ProcessedFile).order_by(desc(ProcessedFile.created_at)).limit(10).all()
    recent_files_data = [
        {
            "id": f.id,
            "filename": f.original_filename,
            "user_email": f.user.email if f.user else "Unknown",
            "status": f.status.value,
            "created_at": f.created_at.isoformat()
        }
        for f in recent_files
    ]
    
    # Get recent users
    recent_users = db.query(User).order_by(desc(User.created_at)).limit(10).all()
    recent_users_data = [
        {
            "id": u.id,
            "email": u.email,
            "tier": u.tier.value,
            "subscription_active": u.subscription_active,
            "created_at": u.created_at.isoformat()
        }
        for u in recent_users
    ]
    
    # Get tier distribution
    tier_counts = db.query(User.tier, func.count(User.id)).group_by(User.tier).all()
    tier_distribution = [
        {"tier": tier.value, "count": count}
        for tier, count in tier_counts
    ]
    
    return {
        "users": {
            "total": total_users,
            "new_30d": new_users_30d,
            "new_7d": new_users_7d,
            "active_subscriptions": active_subscriptions,
            "tier_distribution": tier_distribution
        },
        "files": {
            "total": total_files,
            "processed_30d": files_30d,
            "processed_7d": files_7d,
            "status_distribution": []  # Could add this if needed
        },
        "recent_activity": {
            "recent_files": recent_files_data,
            "recent_users": recent_users_data
        },
        "daily_stats": []  # Would need to calculate this from real data
    }

@app.get("/api/management/revenue")
async def admin_revenue(
    admin_user = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """Get revenue and subscription metrics - real data only"""
    from app.models.database import User
    from datetime import datetime, timedelta
    from sqlalchemy import func
    
    # Basic tier pricing (in dollars)
    tier_prices = {
        "free": 0,
        "basic": 9.99,
        "pro": 29.99,
        "enterprise": 99.99
    }
    
    # Get active users by tier
    active_users = db.query(User).filter(User.subscription_active == True).all()
    
    # Calculate MRR based on real active subscriptions
    mrr = sum(tier_prices.get(u.tier.value, 0) for u in active_users)
    arr = mrr * 12
    
    # Get revenue breakdown by tier
    tier_revenue = []
    for tier, price in tier_prices.items():
        if price > 0:  # Only include paid tiers
            tier_users = db.query(User).filter(
                User.tier == tier,
                User.subscription_active == True
            ).count()
            tier_revenue.append({
                "tier": tier,
                "users": tier_users,
                "monthly_revenue": tier_users * price
            })
    
    # New subscriptions in last 30 days
    thirty_days_ago = datetime.utcnow() - timedelta(days=30)
    new_subscriptions_30d = db.query(User).filter(
        User.subscription_active == True,
        User.created_at >= thirty_days_ago
    ).count()
    
    return {
        "mrr": round(mrr, 2),
        "arr": round(arr, 2),
        "active_subscriptions": len(active_users),
        "new_subscriptions_30d": new_subscriptions_30d,
        "tier_revenue": tier_revenue
    }

@app.get("/api/management/system-health")
async def admin_system_health(
    admin_user = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """Get system health metrics"""
    from sqlalchemy import text
    
    # Database connection test
    try:
        db.execute(text("SELECT 1"))
        db_status = "healthy"
    except Exception as e:
        db_status = f"error: {str(e)}"
    
    return {
        "database": {
            "status": db_status,
            "total_tables": ["users", "processed_files", "api_keys", "usage_logs"]
        },
        "processing": {
            "failed_files_24h": 0,
            "queue_status": "active"
        },
        "uptime": "Running"
    }

@app.get("/api/management/transactions")
async def admin_transactions(
    page: int = 1,
    limit: int = 50,
    search: Optional[str] = None,
    status: Optional[str] = None,
    tier: Optional[str] = None,
    admin_user = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """Get transactions with filtering and pagination - real Stripe data"""
    from app.models.database import User
    import stripe
    from app.core.config import settings
    from datetime import datetime
    
    try:
        # Configure Stripe
        stripe.api_key = settings.STRIPE_SECRET_KEY
        
        # Get all users with Stripe customer IDs
        users_with_stripe = db.query(User).filter(
            User.stripe_customer_id.isnot(None)
        ).all()
        
        all_transactions = []
        
        # Get recent charges from Stripe for each customer
        for user in users_with_stripe:
            try:
                # Get charges for this customer
                charges = stripe.Charge.list(
                    customer=user.stripe_customer_id,
                    limit=100  # Get recent charges
                )
                
                for charge in charges.data:
                    # Only include successful charges
                    if charge.status == 'succeeded':
                        # Get subscription info if available
                        subscription_tier = user.tier.value if user.tier else "free"
                        
                        transaction = {
                            "id": charge.id,
                            "user_id": user.id,
                            "user_name": user.full_name,
                            "user_email": user.email,
                            "amount": charge.amount,  # Amount in cents
                            "currency": charge.currency.upper(),
                            "status": "succeeded",
                            "payment_method": charge.payment_method_details.type if charge.payment_method_details else "card",
                            "subscription_tier": subscription_tier,
                            "billing_period": "monthly",
                            "created_at": datetime.fromtimestamp(charge.created).isoformat(),
                            "updated_at": datetime.fromtimestamp(charge.created).isoformat(),
                            "stripe_payment_intent_id": charge.payment_intent,
                            "stripe_subscription_id": user.subscription_id,
                            "metadata": charge.metadata or {}
                        }
                        all_transactions.append(transaction)
                        
            except Exception as e:
                # Log error but continue with other users
                print(f"Error getting charges for user {user.id}: {str(e)}")
                continue
        
        # Sort by creation date (newest first)
        all_transactions.sort(key=lambda x: x["created_at"], reverse=True)
        
        # Apply filters
        filtered_transactions = all_transactions
        
        if search:
            filtered_transactions = [t for t in filtered_transactions if 
                                   search.lower() in t["user_email"].lower() or 
                                   search.lower() in t["user_name"].lower() or 
                                   search.lower() in t["id"].lower()]
        
        if status:
            filtered_transactions = [t for t in filtered_transactions if t["status"] == status]
        
        if tier:
            filtered_transactions = [t for t in filtered_transactions if t["subscription_tier"] == tier]
        
        # Apply pagination
        total = len(filtered_transactions)
        offset = (page - 1) * limit
        paginated_transactions = filtered_transactions[offset:offset + limit]
        
        return {
            "transactions": paginated_transactions,
            "pagination": {
                "page": page,
                "limit": limit,
                "total": total,
                "pages": (total + limit - 1) // limit if total > 0 else 0
            }
        }
        
    except Exception as e:
        # If Stripe is not configured or there's an error, return empty
        print(f"Error fetching Stripe transactions: {str(e)}")
        return {
            "transactions": [],
            "pagination": {
                "page": page,
                "limit": limit,
                "total": 0,
                "pages": 0
            }
        }

@app.get("/api/management/transactions/stats")
async def admin_transaction_stats(
    admin_user = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """Get transaction statistics - real Stripe data"""
    from app.models.database import User
    import stripe
    from app.core.config import settings
    from datetime import datetime, timedelta
    
    try:
        # Configure Stripe
        stripe.api_key = settings.STRIPE_SECRET_KEY
        
        # Get all users with Stripe customer IDs
        users_with_stripe = db.query(User).filter(
            User.stripe_customer_id.isnot(None)
        ).all()
        
        total_revenue = 0
        monthly_revenue = 0
        total_transactions = 0
        successful_transactions = 0
        failed_transactions = 0
        
        # Calculate date for monthly stats (last 30 days)
        thirty_days_ago = datetime.now() - timedelta(days=30)
        
        # Get charges from Stripe for each customer
        for user in users_with_stripe:
            try:
                # Get all charges for this customer
                charges = stripe.Charge.list(
                    customer=user.stripe_customer_id,
                    limit=100
                )
                
                for charge in charges.data:
                    charge_date = datetime.fromtimestamp(charge.created)
                    
                    # Count all transactions
                    total_transactions += 1
                    
                    if charge.status == 'succeeded':
                        successful_transactions += 1
                        revenue_amount = charge.amount  # Amount in cents
                        total_revenue += revenue_amount
                        
                        # Check if charge is within last 30 days
                        if charge_date >= thirty_days_ago:
                            monthly_revenue += revenue_amount
                    else:
                        failed_transactions += 1
                        
            except Exception as e:
                print(f"Error getting charges for user {user.id}: {str(e)}")
                continue
        
        # Calculate average transaction value
        average_transaction_value = total_revenue // successful_transactions if successful_transactions > 0 else 0
        
        return {
            "total_revenue": total_revenue,
            "monthly_revenue": monthly_revenue,
            "total_transactions": total_transactions,
            "successful_transactions": successful_transactions,
            "failed_transactions": failed_transactions,
            "average_transaction_value": average_transaction_value
        }
        
    except Exception as e:
        # If Stripe is not configured or there's an error, return zeros
        print(f"Error fetching Stripe transaction stats: {str(e)}")
        return {
            "total_revenue": 0,
            "monthly_revenue": 0,
            "total_transactions": 0,
            "successful_transactions": 0,
            "failed_transactions": 0,
            "average_transaction_value": 0
        }

@app.get("/api/management/transactions/export")
async def admin_export_transactions(
    search: Optional[str] = None,
    status: Optional[str] = None,
    tier: Optional[str] = None,
    admin_user = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """Export transactions as CSV - real Stripe data"""
    from fastapi.responses import StreamingResponse
    import io
    import csv
    from datetime import datetime
    from app.models.database import User
    import stripe
    from app.core.config import settings
    
    try:
        # Configure Stripe
        stripe.api_key = settings.STRIPE_SECRET_KEY
        
        # Get all users with Stripe customer IDs
        users_with_stripe = db.query(User).filter(
            User.stripe_customer_id.isnot(None)
        ).all()
        
        all_transactions = []
        
        # Get charges from Stripe for each customer
        for user in users_with_stripe:
            try:
                charges = stripe.Charge.list(
                    customer=user.stripe_customer_id,
                    limit=100
                )
                
                for charge in charges.data:
                    if charge.status == 'succeeded':
                        subscription_tier = user.tier.value if user.tier else "free"
                        
                        transaction = {
                            "id": charge.id,
                            "user_email": user.email,
                            "user_name": user.full_name,
                            "amount": charge.amount / 100,  # Convert cents to dollars
                            "currency": charge.currency.upper(),
                            "status": charge.status,
                            "subscription_tier": subscription_tier,
                            "billing_period": "monthly",
                            "created_at": datetime.fromtimestamp(charge.created).strftime("%Y-%m-%d %H:%M:%S"),
                            "payment_method": charge.payment_method_details.type if charge.payment_method_details else "card"
                        }
                        all_transactions.append(transaction)
                        
            except Exception as e:
                print(f"Error getting charges for user {user.id}: {str(e)}")
                continue
        
        # Sort by creation date (newest first)
        all_transactions.sort(key=lambda x: x["created_at"], reverse=True)
        
        # Apply filters
        filtered_transactions = all_transactions
        if search:
            filtered_transactions = [t for t in filtered_transactions if 
                                   search.lower() in t["user_email"].lower() or 
                                   search.lower() in t["user_name"].lower() or 
                                   search.lower() in t["id"].lower()]
        if status:
            filtered_transactions = [t for t in filtered_transactions if t["status"] == status]
        if tier:
            filtered_transactions = [t for t in filtered_transactions if t["subscription_tier"] == tier]
        
        # Create CSV
        output = io.StringIO()
        fieldnames = ["id", "user_email", "user_name", "amount", "currency", "status", "subscription_tier", "billing_period", "created_at", "payment_method"]
        writer = csv.DictWriter(output, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(filtered_transactions)
        
        # Create streaming response
        response = StreamingResponse(
            io.BytesIO(output.getvalue().encode()),
            media_type="text/csv",
            headers={"Content-Disposition": f"attachment; filename=transactions_{datetime.now().strftime('%Y%m%d')}.csv"}
        )
        return response
        
    except Exception as e:
        print(f"Error exporting Stripe transactions: {str(e)}")
        # Return empty CSV on error
        output = io.StringIO()
        fieldnames = ["id", "user_email", "user_name", "amount", "currency", "status", "subscription_tier", "billing_period", "created_at", "payment_method"]
        writer = csv.DictWriter(output, fieldnames=fieldnames)
        writer.writeheader()
        
        response = StreamingResponse(
            io.BytesIO(output.getvalue().encode()),
            media_type="text/csv",
            headers={"Content-Disposition": f"attachment; filename=transactions_{datetime.now().strftime('%Y%m%d')}.csv"}
        )
        return response

@app.get("/")
async def root():
    return {
        "message": "PDF Table Extractor API",
        "version": "1.0.0",
        "docs": "/docs" if settings.ENVIRONMENT == "development" else None
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.ENVIRONMENT == "development"
    )