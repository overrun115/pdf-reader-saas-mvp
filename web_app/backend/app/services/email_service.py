import os
from typing import Dict, List, Optional
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail, To, From, Subject, HtmlContent, PlainTextContent
from sendgrid.helpers.mail import TrackingSettings, ClickTracking, OpenTracking
from jinja2 import Environment, FileSystemLoader, select_autoescape
from app.core.config import settings
from app.models.database import User, UserTier
import logging

logger = logging.getLogger(__name__)

class EmailService:
    """Service for sending emails using SendGrid"""
    
    def __init__(self):
        self.sg_client = None
        if settings.SENDGRID_API_KEY:
            self.sg_client = SendGridAPIClient(api_key=settings.SENDGRID_API_KEY)
        else:
            logger.warning("SendGrid API key not configured. Emails will not be sent.")
        
        # Setup Jinja2 for email templates
        template_dir = os.path.join(os.path.dirname(__file__), '..', 'templates', 'emails')
        self.jinja_env = Environment(
            loader=FileSystemLoader(template_dir),
            autoescape=select_autoescape(['html', 'xml'])
        )
    
    async def send_email(
        self,
        to_email: str,
        to_name: str,
        subject: str,
        html_content: str,
        plain_content: Optional[str] = None
    ) -> bool:
        """Send an email using SendGrid"""
        if not self.sg_client:
            logger.warning(f"Cannot send email to {to_email}: SendGrid not configured")
            return False
        
        try:
            from_email = From(settings.FROM_EMAIL, settings.FROM_NAME)
            to_email_obj = To(to_email, to_name)
            subject_obj = Subject(subject)
            html_content_obj = HtmlContent(html_content)
            
            mail = Mail(
                from_email=from_email,
                to_emails=to_email_obj,
                subject=subject_obj,
                html_content=html_content_obj
            )
            
            # Disable click tracking to avoid SSL issues with SendGrid domains
            tracking_settings = TrackingSettings()
            tracking_settings.click_tracking = ClickTracking(enable=False)
            tracking_settings.open_tracking = OpenTracking(enable=False)
            mail.tracking_settings = tracking_settings
            
            if plain_content:
                mail.plain_text_content = PlainTextContent(plain_content)
            
            response = self.sg_client.send(mail)
            
            if response.status_code >= 200 and response.status_code < 300:
                logger.info(f"Email sent successfully to {to_email}")
                return True
            else:
                logger.error(f"Failed to send email to {to_email}: Status {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"Error sending email to {to_email}: {str(e)}")
            return False
    
    def render_template(self, template_name: str, context: Dict) -> tuple[str, str]:
        """Render HTML and plain text versions of an email template"""
        try:
            # Render HTML template
            html_template = self.jinja_env.get_template(f"{template_name}.html")
            html_content = html_template.render(**context)
            
            # Try to render plain text template
            try:
                text_template = self.jinja_env.get_template(f"{template_name}.txt")
                plain_content = text_template.render(**context)
            except:
                # If no plain text template, create basic version
                plain_content = self._html_to_plain(html_content)
            
            return html_content, plain_content
            
        except Exception as e:
            logger.error(f"Error rendering template {template_name}: {str(e)}")
            raise
    
    def _html_to_plain(self, html_content: str) -> str:
        """Convert HTML to plain text (basic implementation)"""
        import re
        # Remove HTML tags
        plain = re.sub(r'<[^>]+>', '', html_content)
        # Clean up whitespace
        plain = re.sub(r'\s+', ' ', plain).strip()
        return plain
    
    async def send_welcome_email(self, user: User) -> bool:
        """Send welcome email to new user"""
        context = {
            'user_name': user.full_name,
            'user_email': user.email,
            'dashboard_url': f"{settings.FRONTEND_URL}/dashboard",
            'support_email': settings.FROM_EMAIL,
            'tier': user.tier.value
        }
        
        try:
            html_content, plain_content = self.render_template('welcome', context)
            
            return await self.send_email(
                to_email=user.email,
                to_name=user.full_name,
                subject="Welcome to PDF Extractor! 🎉",
                html_content=html_content,
                plain_content=plain_content
            )
        except Exception as e:
            logger.error(f"Error sending welcome email to {user.email}: {str(e)}")
            return False
    
    async def send_subscription_confirmation_email(self, user: User, plan_name: str, amount: float) -> bool:
        """Send subscription confirmation email"""
        context = {
            'user_name': user.full_name,
            'plan_name': plan_name,
            'amount': amount,
            'tier': user.tier.value,
            'dashboard_url': f"{settings.FRONTEND_URL}/dashboard",
            'billing_url': f"{settings.FRONTEND_URL}/subscription",
            'support_email': settings.FROM_EMAIL
        }
        
        try:
            html_content, plain_content = self.render_template('subscription_confirmation', context)
            
            return await self.send_email(
                to_email=user.email,
                to_name=user.full_name,
                subject=f"Subscription Confirmed - {plan_name} Plan",
                html_content=html_content,
                plain_content=plain_content
            )
        except Exception as e:
            logger.error(f"Error sending subscription confirmation email to {user.email}: {str(e)}")
            return False
    
    async def send_usage_limit_warning_email(self, user: User, usage_percentage: int) -> bool:
        """Send usage limit warning email"""
        tier_limits = {
            UserTier.FREE: 5,
            UserTier.BASIC: 50,
            UserTier.PRO: 200,
            UserTier.ENTERPRISE: -1
        }
        
        limit = tier_limits.get(user.tier, 5)
        remaining = max(0, limit - user.files_processed_this_month) if limit > 0 else -1
        
        context = {
            'user_name': user.full_name,
            'usage_percentage': usage_percentage,
            'files_used': user.files_processed_this_month,
            'files_limit': limit,
            'files_remaining': remaining,
            'tier': user.tier.value,
            'upgrade_url': f"{settings.FRONTEND_URL}/subscription",
            'dashboard_url': f"{settings.FRONTEND_URL}/dashboard",
            'support_email': settings.FROM_EMAIL
        }
        
        try:
            html_content, plain_content = self.render_template('usage_warning', context)
            
            return await self.send_email(
                to_email=user.email,
                to_name=user.full_name,
                subject="⚠️ Approaching Monthly Usage Limit",
                html_content=html_content,
                plain_content=plain_content
            )
        except Exception as e:
            logger.error(f"Error sending usage warning email to {user.email}: {str(e)}")
            return False
    
    async def send_subscription_cancelled_email(self, user: User, end_date: str) -> bool:
        """Send subscription cancellation email"""
        context = {
            'user_name': user.full_name,
            'end_date': end_date,
            'tier': user.tier.value,
            'reactivate_url': f"{settings.FRONTEND_URL}/subscription",
            'dashboard_url': f"{settings.FRONTEND_URL}/dashboard",
            'support_email': settings.FROM_EMAIL
        }
        
        try:
            html_content, plain_content = self.render_template('subscription_cancelled', context)
            
            return await self.send_email(
                to_email=user.email,
                to_name=user.full_name,
                subject="Subscription Cancelled - We're Sorry to See You Go",
                html_content=html_content,
                plain_content=plain_content
            )
        except Exception as e:
            logger.error(f"Error sending cancellation email to {user.email}: {str(e)}")
            return False
    
    async def send_payment_failed_email(self, user: User, retry_date: str) -> bool:
        """Send payment failed email"""
        context = {
            'user_name': user.full_name,
            'retry_date': retry_date,
            'tier': user.tier.value,
            'billing_url': f"{settings.FRONTEND_URL}/subscription",
            'support_email': settings.FROM_EMAIL
        }
        
        try:
            html_content, plain_content = self.render_template('payment_failed', context)
            
            return await self.send_email(
                to_email=user.email,
                to_name=user.full_name,
                subject="🚨 Payment Failed - Action Required",
                html_content=html_content,
                plain_content=plain_content
            )
        except Exception as e:
            logger.error(f"Error sending payment failed email to {user.email}: {str(e)}")
            return False

    async def send_email_verification(self, user: User, verification_token: str) -> bool:
        """Send email verification email"""
        verification_url = f"{settings.FRONTEND_URL}/verify-email?token={verification_token}"
        
        context = {
            'user_name': user.full_name,
            'user_email': user.email,
            'verification_url': verification_url,
            'verification_token': verification_token,
            'support_email': settings.FROM_EMAIL,
            'frontend_url': settings.FRONTEND_URL
        }
        
        try:
            html_content, plain_content = self.render_template('email_verification', context)
            
            return await self.send_email(
                to_email=user.email,
                to_name=user.full_name,
                subject="Verify your email address - PDF Extractor",
                html_content=html_content,
                plain_content=plain_content
            )
        except Exception as e:
            logger.error(f"Error sending verification email to {user.email}: {str(e)}")
            return False
    
    async def send_password_reset_email(self, user: User, reset_token: str) -> bool:
        """Send password reset email"""
        reset_url = f"{settings.FRONTEND_URL}/reset-password?token={reset_token}"
        
        context = {
            'user_name': user.full_name,
            'user_email': user.email,
            'reset_url': reset_url,
            'reset_token': reset_token,
            'support_email': settings.FROM_EMAIL,
            'frontend_url': settings.FRONTEND_URL
        }
        
        try:
            html_content, plain_content = self.render_template('password_reset', context)
            
            return await self.send_email(
                to_email=user.email,
                to_name=user.full_name,
                subject="Reset your password - PDF Extractor",
                html_content=html_content,
                plain_content=plain_content
            )
        except Exception as e:
            logger.error(f"Error sending password reset email to {user.email}: {str(e)}")
            return False

# Create service instance
email_service = EmailService()