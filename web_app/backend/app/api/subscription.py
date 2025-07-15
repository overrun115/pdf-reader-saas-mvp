from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.api.dependencies import get_current_user
from app.models.database import User, UserTier
from app.models.schemas import (
    SubscriptionPlan, CreateCheckoutRequest, CheckoutResponse,
    BillingPortalRequest, BillingPortalResponse, SubscriptionStatus,
    ResponseModel
)
from app.services.stripe_service import stripe_service
from typing import List
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/subscription", tags=["subscription"])

# Available subscription plans
SUBSCRIPTION_PLANS = [
    SubscriptionPlan(
        tier="free",
        name="Free Plan",
        price=0.0,
        price_id="",  # Will be set from config
        features=[
            "5 files per month",
            "Basic table extraction",
            "CSV export",
            "Email support"
        ],
        files_per_month=5
    ),
    SubscriptionPlan(
        tier="basic",
        name="Basic Plan",
        price=9.99,
        price_id="",  # Will be set from config
        features=[
            "50 files per month",
            "Advanced table extraction",
            "CSV & Excel export",
            "Email support",
            "API access"
        ],
        files_per_month=50
    ),
    SubscriptionPlan(
        tier="pro",
        name="Pro Plan",
        price=29.99,
        price_id="",  # Will be set from config
        features=[
            "200 files per month",
            "Premium table extraction",
            "CSV & Excel export",
            "Priority support",
            "API access",
            "Batch processing"
        ],
        files_per_month=200
    ),
    SubscriptionPlan(
        tier="enterprise",
        name="Enterprise Plan",
        price=99.99,
        price_id="",  # Will be set from config
        features=[
            "Unlimited files",
            "Premium table extraction",
            "All export formats",
            "Dedicated support",
            "API access",
            "Batch processing",
            "Custom integrations"
        ],
        files_per_month=-1  # Unlimited
    )
]

@router.get("/plans", response_model=List[SubscriptionPlan])
async def get_subscription_plans():
    """Get all available subscription plans"""
    from app.core.config import settings
    
    # Update price IDs from configuration
    plans = SUBSCRIPTION_PLANS.copy()
    plans[0].price_id = settings.STRIPE_PRICE_FREE or ""
    plans[1].price_id = settings.STRIPE_PRICE_BASIC or ""
    plans[2].price_id = settings.STRIPE_PRICE_PRO or ""
    plans[3].price_id = settings.STRIPE_PRICE_ENTERPRISE or ""
    
    return plans

@router.get("/status", response_model=SubscriptionStatus)
async def get_subscription_status(
    current_user: User = Depends(get_current_user)
):
    """Get current user's subscription status"""
    return SubscriptionStatus(
        tier=current_user.tier,
        subscription_active=current_user.subscription_active,
        subscription_id=current_user.subscription_id,
        subscription_end_date=current_user.subscription_end_date,
        stripe_customer_id=current_user.stripe_customer_id
    )

@router.post("/create-checkout", response_model=CheckoutResponse)
async def create_checkout_session(
    request: CreateCheckoutRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a Stripe checkout session for subscription"""
    from app.core.config import settings
    
    # Check if Stripe is configured
    if not settings.STRIPE_SECRET_KEY:
        raise HTTPException(
            status_code=503,
            detail="Stripe billing is not configured. Please contact support."
        )
    
    try:
        # Check if user already has a Stripe customer ID
        if not current_user.stripe_customer_id:
            # Create Stripe customer
            customer = await stripe_service.create_customer(
                email=current_user.email,
                name=current_user.full_name,
                user_id=current_user.id
            )
            
            # Update user with Stripe customer ID
            current_user.stripe_customer_id = customer.id
            db.commit()
            db.refresh(current_user)
        
        # Create checkout session
        session = await stripe_service.create_checkout_session(
            customer_id=current_user.stripe_customer_id,
            price_id=request.price_id,
            success_url=request.success_url,
            cancel_url=request.cancel_url,
            user_id=current_user.id
        )
        
        return CheckoutResponse(
            checkout_url=session.url,
            session_id=session.id
        )
        
    except Exception as e:
        logger.error(f"Failed to create checkout session for user {current_user.id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to create checkout session")

@router.post("/create-billing-portal", response_model=BillingPortalResponse)
async def create_billing_portal_session(
    request: BillingPortalRequest,
    current_user: User = Depends(get_current_user)
):
    """Create a Stripe billing portal session for subscription management"""
    from app.core.config import settings
    
    logger.info(f"Creating billing portal for user {current_user.id} ({current_user.email})")
    
    # Check if Stripe is configured
    if not settings.STRIPE_SECRET_KEY:
        logger.error("Stripe secret key not configured")
        raise HTTPException(
            status_code=503,
            detail="Stripe billing is not configured. Please contact support."
        )
    
    try:
        if not current_user.stripe_customer_id:
            logger.error(f"User {current_user.id} has no stripe_customer_id")
            raise HTTPException(
                status_code=400, 
                detail="No Stripe customer found. Please subscribe first."
            )
        
        logger.info(f"Creating billing portal for customer: {current_user.stripe_customer_id}")
        
        # Create billing portal session
        session = await stripe_service.create_billing_portal_session(
            customer_id=current_user.stripe_customer_id,
            return_url=request.return_url
        )
        
        logger.info(f"Successfully created billing portal session: {session.id}")
        return BillingPortalResponse(portal_url=session.url)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to create billing portal for user {current_user.id}: {str(e)}")
        logger.error(f"Exception type: {type(e)}")
        logger.error(f"Exception args: {e.args}")
        raise HTTPException(status_code=500, detail=f"Failed to create billing portal: {str(e)}")

@router.post("/cancel")
async def cancel_subscription(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Cancel current subscription"""
    try:
        if not current_user.subscription_id:
            raise HTTPException(status_code=400, detail="No active subscription found")
        
        # Cancel subscription in Stripe
        await stripe_service.cancel_subscription(current_user.subscription_id)
        
        # Update user in database - don't immediately downgrade, let it expire
        current_user.subscription_active = False
        db.commit()
        
        return ResponseModel(
            success=True,
            message="Subscription cancelled successfully. Access will continue until the end of your billing period."
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to cancel subscription for user {current_user.id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to cancel subscription")

@router.get("/usage")
async def get_usage_info(current_user: User = Depends(get_current_user)):
    """Get current usage information for the user"""
    from app.core.config import settings
    
    # Get tier limits
    tier_limits = {
        UserTier.FREE: settings.FREE_TIER_LIMIT,
        UserTier.BASIC: settings.BASIC_TIER_LIMIT,
        UserTier.PRO: settings.PRO_TIER_LIMIT,
        UserTier.ENTERPRISE: settings.ENTERPRISE_TIER_LIMIT,
    }
    
    tier_limit = tier_limits.get(current_user.tier, settings.FREE_TIER_LIMIT)
    remaining = tier_limit - current_user.files_processed_this_month if tier_limit > 0 else -1
    
    return {
        "current_tier": current_user.tier,
        "files_processed_this_month": current_user.files_processed_this_month,
        "tier_limit": tier_limit,
        "remaining_files": remaining,
        "subscription_active": current_user.subscription_active,
        "subscription_end_date": current_user.subscription_end_date
    }