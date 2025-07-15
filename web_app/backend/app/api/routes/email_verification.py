from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
import secrets
from pydantic import BaseModel

from app.core.database import get_db
from app.api.dependencies import get_current_active_user
from app.models.database import User
from app.services.email_service import email_service
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

class ResendVerificationRequest(BaseModel):
    email: str

class VerifyEmailRequest(BaseModel):
    token: str

class PasswordResetRequest(BaseModel):
    email: str

class PasswordResetConfirmRequest(BaseModel):
    token: str
    new_password: str

@router.get("/test")
async def test_endpoint():
    """Test endpoint"""
    return {"message": "Email verification endpoint is working", "timestamp": "2025-07-10-14:47"}

@router.post("/verify-email-simple")
async def verify_email_simple(
    request: VerifyEmailRequest,
    db: Session = Depends(get_db)
):
    """Simple email verification endpoint using raw SQL"""
    try:
        from sqlalchemy import text
        
        # Find user with raw SQL
        result = db.execute(
            text("SELECT id, email, is_verified FROM users WHERE email_verification_token = :token"),
            {"token": request.token}
        ).fetchone()
        
        if not result:
            return {"error": "Token not found", "token_preview": request.token[:20]}
        
        user_id, email, is_verified = result
        
        if is_verified:
            return {"message": "Already verified", "email": email}
        
        # Update user with raw SQL
        db.execute(
            text("""UPDATE users 
                    SET is_verified = 1, 
                        email_verification_token = NULL, 
                        email_verification_token_expires = NULL,
                        updated_at = CURRENT_TIMESTAMP
                    WHERE id = :user_id"""),
            {"user_id": user_id}
        )
        db.commit()
        
        return {"message": "Verified successfully", "email": email}
        
    except Exception as e:
        return {"error": str(e), "type": type(e).__name__}

@router.post("/send-verification")
async def send_verification_email(
    request: ResendVerificationRequest,
    db: Session = Depends(get_db)
):
    """Send or resend email verification"""
    # Find user by email
    user = db.query(User).filter(User.email == request.email).first()
    if not user:
        # Don't reveal if email exists or not for security
        return {"message": "If the email exists, a verification link has been sent."}
    
    # Check if already verified
    if user.is_verified:
        return {"message": "Email is already verified."}
    
    # Generate verification token
    verification_token = secrets.token_urlsafe(32)
    token_expires = datetime.utcnow() + timedelta(hours=24)
    
    # Update user with token
    user.email_verification_token = verification_token
    user.email_verification_token_expires = token_expires
    db.commit()
    
    # Send verification email
    try:
        await email_service.send_email_verification(user, verification_token)
        return {"message": "Verification email sent successfully."}
    except Exception as e:
        logger.error(f"Failed to send verification email: {str(e)}")
        return {"message": "Failed to send verification email. Please try again later."}

@router.post("/verify-email")
async def verify_email(
    request: VerifyEmailRequest,
    db: Session = Depends(get_db)
):
    """Verify email address with token"""
    try:
        # Find user by verification token
        user = db.query(User).filter(
            User.email_verification_token == request.token
        ).first()
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid verification token. Please check your email for the correct link."
            )
        
        # Check if already verified
        if user.is_verified:
            return {"message": "Email is already verified!"}
        
        # Check if token is expired
        if user.email_verification_token_expires:
            # Handle both string and datetime objects
            if isinstance(user.email_verification_token_expires, str):
                try:
                    expires_dt = datetime.fromisoformat(user.email_verification_token_expires.replace('Z', '+00:00') if user.email_verification_token_expires.endswith('Z') else user.email_verification_token_expires)
                except ValueError:
                    expires_dt = datetime.strptime(user.email_verification_token_expires, '%Y-%m-%d %H:%M:%S.%f')
            else:
                expires_dt = user.email_verification_token_expires
            
            if expires_dt <= datetime.utcnow():
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Verification token has expired. Please request a new verification email."
                )
        
        # Mark user as verified
        user.is_verified = True
        user.email_verification_token = None
        user.email_verification_token_expires = None
        db.commit()
        
        # Send welcome email
        try:
            await email_service.send_welcome_email(user)
        except Exception as e:
            logger.error(f"Failed to send welcome email: {str(e)}")
        
        return {"message": "Email verified successfully!"}
    
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        logger.error(f"Error during email verification: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred during verification. Please try again later."
        )

@router.post("/resend-verification")
async def resend_verification_email(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Resend verification email to current user"""
    # Check if already verified
    if current_user.is_verified:
        return {"message": "Email is already verified."}
    
    # Generate new verification token
    verification_token = secrets.token_urlsafe(32)
    token_expires = datetime.utcnow() + timedelta(hours=24)
    
    # Update user with token
    current_user.email_verification_token = verification_token
    current_user.email_verification_token_expires = token_expires
    db.commit()
    
    # Send verification email
    try:
        await email_service.send_email_verification(current_user, verification_token)
        return {"message": "Verification email sent successfully."}
    except Exception as e:
        logger.error(f"Failed to send verification email: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to send verification email. Please try again later."
        )

@router.post("/forgot-password")
async def forgot_password(
    request: PasswordResetRequest,
    db: Session = Depends(get_db)
):
    """Send password reset email"""
    # Find user by email
    user = db.query(User).filter(User.email == request.email).first()
    if not user:
        # Don't reveal if email exists or not for security
        return {"message": "If the email exists, a password reset link has been sent."}
    
    # Generate reset token
    reset_token = secrets.token_urlsafe(32)
    token_expires = datetime.utcnow() + timedelta(hours=1)  # 1 hour expiry for security
    
    # Update user with token
    user.password_reset_token = reset_token
    user.password_reset_token_expires = token_expires
    db.commit()
    
    # Send password reset email
    try:
        await email_service.send_password_reset_email(user, reset_token)
        return {"message": "Password reset link sent successfully."}
    except Exception as e:
        logger.error(f"Failed to send password reset email: {str(e)}")
        return {"message": "Failed to send password reset email. Please try again later."}

@router.post("/reset-password")
async def reset_password(
    request: PasswordResetConfirmRequest,
    db: Session = Depends(get_db)
):
    """Reset password with token"""
    from app.core.security import get_password_hash
    
    # Find user by reset token
    user = db.query(User).filter(
        User.password_reset_token == request.token,
        User.password_reset_token_expires > datetime.utcnow()
    ).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired reset token"
        )
    
    # Hash new password
    hashed_password = get_password_hash(request.new_password)
    
    # Update user password and clear reset token
    user.hashed_password = hashed_password
    user.password_reset_token = None
    user.password_reset_token_expires = None
    db.commit()
    
    return {"message": "Password reset successfully!"}

@router.get("/verification-status")
async def get_verification_status(
    current_user: User = Depends(get_current_active_user)
):
    """Get current user's email verification status"""
    return {
        "is_verified": current_user.is_verified,
        "email": current_user.email,
        "has_pending_verification": current_user.email_verification_token is not None
    }