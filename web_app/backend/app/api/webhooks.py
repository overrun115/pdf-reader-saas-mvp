from fastapi import APIRouter, Request, HTTPException, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.database import User, UserTier
from app.services.stripe_service import stripe_service
from app.services.email_service import email_service
from datetime import datetime, timezone
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/webhooks", tags=["webhooks"])

@router.post("/stripe")
async def stripe_webhook(
    request: Request,
    db: Session = Depends(get_db)
):
    """Handle Stripe webhooks"""
    try:
        # Get the request body and signature
        payload = await request.body()
        sig_header = request.headers.get('stripe-signature')
        
        if not sig_header:
            raise HTTPException(status_code=400, detail="Missing Stripe signature")
        
        # Construct the webhook event
        event = stripe_service.construct_webhook_event(payload, sig_header)
        
        logger.info(f"Received Stripe webhook: {event['type']}")
        
        # Handle different event types
        if event['type'] == 'customer.subscription.created':
            await handle_subscription_created(event['data']['object'], db)
        
        elif event['type'] == 'customer.subscription.updated':
            await handle_subscription_updated(event['data']['object'], db)
        
        elif event['type'] == 'customer.subscription.deleted':
            await handle_subscription_deleted(event['data']['object'], db)
        
        elif event['type'] == 'invoice.payment_succeeded':
            await handle_payment_succeeded(event['data']['object'], db)
        
        elif event['type'] == 'invoice.payment_failed':
            await handle_payment_failed(event['data']['object'], db)
        
        elif event['type'] == 'checkout.session.completed':
            await handle_checkout_completed(event['data']['object'], db)
        
        else:
            logger.info(f"Unhandled webhook event type: {event['type']}")
        
        return {"status": "success"}
        
    except Exception as e:
        logger.error(f"Stripe webhook error: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))

async def handle_subscription_created(subscription, db: Session):
    """Handle subscription creation"""
    try:
        customer_id = subscription['customer']
        subscription_id = subscription['id']
        
        # Find user by Stripe customer ID
        user = db.query(User).filter(User.stripe_customer_id == customer_id).first()
        if not user:
            logger.error(f"User not found for customer {customer_id}")
            return
        
        # Get the price ID to determine tier
        price_id = subscription['items']['data'][0]['price']['id']
        new_tier = stripe_service.get_tier_for_price_id(price_id)
        
        if new_tier:
            # Update user subscription info
            user.subscription_id = subscription_id
            user.subscription_active = subscription['status'] == 'active'
            user.tier = new_tier
            
            # Set subscription end date
            if subscription.get('current_period_end'):
                user.subscription_end_date = datetime.fromtimestamp(
                    subscription['current_period_end'], 
                    tz=timezone.utc
                )
            
            db.commit()
            logger.info(f"Updated user {user.id} subscription to {new_tier}")
            
            # Send subscription confirmation email
            try:
                plan_names = {
                    UserTier.BASIC: "Basic Plan",
                    UserTier.PRO: "Pro Plan", 
                    UserTier.ENTERPRISE: "Enterprise Plan"
                }
                plan_prices = {
                    UserTier.BASIC: 9.99,
                    UserTier.PRO: 29.99,
                    UserTier.ENTERPRISE: 99.99
                }
                
                plan_name = plan_names.get(new_tier, "Subscription")
                amount = plan_prices.get(new_tier, 0.0)
                
                await email_service.send_subscription_confirmation_email(user, plan_name, amount)
            except Exception as e:
                logger.error(f"Failed to send subscription confirmation email: {str(e)}")
            
    except Exception as e:
        logger.error(f"Error handling subscription created: {str(e)}")
        db.rollback()

async def handle_subscription_updated(subscription, db: Session):
    """Handle subscription updates"""
    try:
        subscription_id = subscription['id']
        
        # Find user by subscription ID
        user = db.query(User).filter(User.subscription_id == subscription_id).first()
        if not user:
            logger.error(f"User not found for subscription {subscription_id}")
            return
        
        # Update subscription status
        user.subscription_active = subscription['status'] == 'active'
        
        # Update tier if price changed
        price_id = subscription['items']['data'][0]['price']['id']
        new_tier = stripe_service.get_tier_for_price_id(price_id)
        
        if new_tier and new_tier != user.tier:
            old_tier = user.tier
            user.tier = new_tier
            logger.info(f"User {user.id} tier changed from {old_tier} to {new_tier}")
        
        # Update subscription end date
        if subscription.get('current_period_end'):
            user.subscription_end_date = datetime.fromtimestamp(
                subscription['current_period_end'], 
                tz=timezone.utc
            )
        
        db.commit()
        logger.info(f"Updated subscription {subscription_id} for user {user.id}")
        
    except Exception as e:
        logger.error(f"Error handling subscription updated: {str(e)}")
        db.rollback()

async def handle_subscription_deleted(subscription, db: Session):
    """Handle subscription cancellation"""
    try:
        subscription_id = subscription['id']
        
        # Find user by subscription ID
        user = db.query(User).filter(User.subscription_id == subscription_id).first()
        if not user:
            logger.error(f"User not found for subscription {subscription_id}")
            return
        
        # Downgrade to free tier
        old_tier = user.tier
        user.tier = UserTier.FREE
        user.subscription_active = False
        user.subscription_id = None
        user.subscription_end_date = None
        
        db.commit()
        logger.info(f"Downgraded user {user.id} from {old_tier} to FREE")
        
        # Send subscription cancelled email
        try:
            # Use subscription end date if available, otherwise use current date
            end_date = "immediately"
            if subscription.get('current_period_end'):
                end_date_obj = datetime.fromtimestamp(
                    subscription['current_period_end'], 
                    tz=timezone.utc
                )
                end_date = end_date_obj.strftime('%B %d, %Y')
            
            await email_service.send_subscription_cancelled_email(user, end_date)
        except Exception as e:
            logger.error(f"Failed to send cancellation email: {str(e)}")
        
    except Exception as e:
        logger.error(f"Error handling subscription deleted: {str(e)}")
        db.rollback()

async def handle_payment_succeeded(invoice, db: Session):
    """Handle successful payment"""
    try:
        customer_id = invoice['customer']
        subscription_id = invoice.get('subscription')
        
        if not subscription_id:
            return  # Not a subscription payment
        
        # Find user by customer ID
        user = db.query(User).filter(User.stripe_customer_id == customer_id).first()
        if not user:
            logger.error(f"User not found for customer {customer_id}")
            return
        
        # Ensure subscription is active
        user.subscription_active = True
        
        # Reset monthly usage on successful payment (new billing period)
        user.files_processed_this_month = 0
        
        db.commit()
        logger.info(f"Payment succeeded for user {user.id}")
        
        # Payment confirmation is handled by subscription_created/updated events
        
    except Exception as e:
        logger.error(f"Error handling payment succeeded: {str(e)}")
        db.rollback()

async def handle_payment_failed(invoice, db: Session):
    """Handle failed payment"""
    try:
        customer_id = invoice['customer']
        subscription_id = invoice.get('subscription')
        
        if not subscription_id:
            return  # Not a subscription payment
        
        # Find user by customer ID
        user = db.query(User).filter(User.stripe_customer_id == customer_id).first()
        if not user:
            logger.error(f"User not found for customer {customer_id}")
            return
        
        logger.warning(f"Payment failed for user {user.id}")
        
        # Send payment failed email
        try:
            # Calculate retry date (usually 3-7 days from Stripe)
            retry_date = "in a few days"
            if invoice.get('next_payment_attempt'):
                retry_date_obj = datetime.fromtimestamp(
                    invoice['next_payment_attempt'], 
                    tz=timezone.utc
                )
                retry_date = retry_date_obj.strftime('%B %d, %Y')
            
            await email_service.send_payment_failed_email(user, retry_date)
        except Exception as e:
            logger.error(f"Failed to send payment failed email: {str(e)}")
            
        # TODO: Implement grace period logic before downgrading
        
    except Exception as e:
        logger.error(f"Error handling payment failed: {str(e)}")

async def handle_checkout_completed(session, db: Session):
    """Handle completed checkout session"""
    try:
        customer_id = session['customer']
        subscription_id = session.get('subscription')
        
        if not subscription_id:
            return  # Not a subscription checkout
        
        # Find user by customer ID
        user = db.query(User).filter(User.stripe_customer_id == customer_id).first()
        if not user:
            logger.error(f"User not found for customer {customer_id}")
            return
        
        logger.info(f"Checkout completed for user {user.id}")
        
        # The subscription webhook will handle the actual subscription updates
        # This is just for logging/analytics
        
    except Exception as e:
        logger.error(f"Error handling checkout completed: {str(e)}")