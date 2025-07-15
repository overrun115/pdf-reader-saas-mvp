import stripe
from typing import Optional, Dict, Any
from app.core.config import settings
from app.models.database import UserTier
import logging

logger = logging.getLogger(__name__)

# Configure Stripe
stripe.api_key = settings.STRIPE_SECRET_KEY

class StripeService:
    """Service for handling Stripe payment operations"""
    
    def __init__(self):
        if not settings.STRIPE_SECRET_KEY:
            logger.warning("Stripe secret key not configured")
    
    @staticmethod
    def get_price_id_for_tier(tier: UserTier) -> Optional[str]:
        """Get Stripe price ID for a given user tier"""
        price_mapping = {
            UserTier.FREE: settings.STRIPE_PRICE_FREE,
            UserTier.BASIC: settings.STRIPE_PRICE_BASIC,
            UserTier.PRO: settings.STRIPE_PRICE_PRO,
            UserTier.ENTERPRISE: settings.STRIPE_PRICE_ENTERPRISE,
        }
        return price_mapping.get(tier)
    
    @staticmethod
    def get_tier_for_price_id(price_id: str) -> Optional[UserTier]:
        """Get user tier for a given Stripe price ID"""
        tier_mapping = {
            settings.STRIPE_PRICE_FREE: UserTier.FREE,
            settings.STRIPE_PRICE_BASIC: UserTier.BASIC,
            settings.STRIPE_PRICE_PRO: UserTier.PRO,
            settings.STRIPE_PRICE_ENTERPRISE: UserTier.ENTERPRISE,
        }
        return tier_mapping.get(price_id)
    
    async def create_customer(self, email: str, name: str, user_id: int) -> Dict[str, Any]:
        """Create a new Stripe customer"""
        try:
            customer = stripe.Customer.create(
                email=email,
                name=name,
                metadata={
                    "user_id": str(user_id)
                }
            )
            logger.info(f"Created Stripe customer {customer.id} for user {user_id}")
            return customer
        except stripe.error.StripeError as e:
            logger.error(f"Failed to create Stripe customer: {str(e)}")
            raise
    
    async def create_checkout_session(
        self,
        customer_id: str,
        price_id: str,
        success_url: str,
        cancel_url: str,
        user_id: int
    ) -> Dict[str, Any]:
        """Create a Stripe checkout session for subscription"""
        try:
            session = stripe.checkout.Session.create(
                customer=customer_id,
                payment_method_types=['card'],
                mode='subscription',
                line_items=[{
                    'price': price_id,
                    'quantity': 1,
                }],
                success_url=success_url,
                cancel_url=cancel_url,
                metadata={
                    "user_id": str(user_id)
                },
                allow_promotion_codes=True,
                billing_address_collection='required',
            )
            logger.info(f"Created checkout session {session.id} for user {user_id}")
            return session
        except stripe.error.StripeError as e:
            logger.error(f"Failed to create checkout session: {str(e)}")
            raise
    
    async def create_billing_portal_session(
        self,
        customer_id: str,
        return_url: str
    ) -> Dict[str, Any]:
        """Create a Stripe billing portal session"""
        try:
            session = stripe.billing_portal.Session.create(
                customer=customer_id,
                return_url=return_url,
            )
            logger.info(f"Created billing portal session for customer {customer_id}")
            return session
        except stripe.error.StripeError as e:
            logger.error(f"Failed to create billing portal session: {str(e)}")
            raise
    
    async def get_subscription(self, subscription_id: str) -> Dict[str, Any]:
        """Get subscription details from Stripe"""
        try:
            subscription = stripe.Subscription.retrieve(subscription_id)
            return subscription
        except stripe.error.StripeError as e:
            logger.error(f"Failed to retrieve subscription {subscription_id}: {str(e)}")
            raise
    
    async def cancel_subscription(self, subscription_id: str) -> Dict[str, Any]:
        """Cancel a subscription immediately"""
        try:
            subscription = stripe.Subscription.delete(subscription_id)
            logger.info(f"Cancelled subscription {subscription_id}")
            return subscription
        except stripe.error.StripeError as e:
            logger.error(f"Failed to cancel subscription {subscription_id}: {str(e)}")
            raise
    
    async def update_subscription(
        self,
        subscription_id: str,
        new_price_id: str
    ) -> Dict[str, Any]:
        """Update subscription to a new price/plan"""
        try:
            # Get current subscription
            subscription = stripe.Subscription.retrieve(subscription_id)
            
            # Update the subscription
            updated_subscription = stripe.Subscription.modify(
                subscription_id,
                items=[{
                    'id': subscription['items']['data'][0].id,
                    'price': new_price_id,
                }],
                proration_behavior='immediate_with_invoice',
            )
            
            logger.info(f"Updated subscription {subscription_id} to price {new_price_id}")
            return updated_subscription
        except stripe.error.StripeError as e:
            logger.error(f"Failed to update subscription {subscription_id}: {str(e)}")
            raise
    
    async def get_customer_subscriptions(self, customer_id: str) -> Dict[str, Any]:
        """Get all subscriptions for a customer"""
        try:
            subscriptions = stripe.Subscription.list(
                customer=customer_id,
                status='active'
            )
            return subscriptions
        except stripe.error.StripeError as e:
            logger.error(f"Failed to get subscriptions for customer {customer_id}: {str(e)}")
            raise
    
    @staticmethod
    def construct_webhook_event(payload: bytes, sig_header: str) -> Dict[str, Any]:
        """Construct and verify webhook event from Stripe"""
        try:
            event = stripe.Webhook.construct_event(
                payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
            )
            return event
        except ValueError as e:
            logger.error(f"Invalid payload in webhook: {str(e)}")
            raise
        except stripe.error.SignatureVerificationError as e:
            logger.error(f"Invalid signature in webhook: {str(e)}")
            raise

# Create service instance
stripe_service = StripeService()