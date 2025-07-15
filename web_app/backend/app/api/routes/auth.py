from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import timedelta

from app.core.database import get_db
from app.core.security import verify_password, create_access_token, verify_reset_token, get_password_hash
from app.core.config import settings
from app.models.schemas import (
    UserCreate, UserResponse, UserLogin, Token, 
    PasswordResetRequest, PasswordReset, ResponseModel
)
from app.services.user_service import (
    get_user_by_email, create_user, update_user_last_login
)
from app.services.email_service import email_service
import secrets
import logging

router = APIRouter()

@router.post("/register", response_model=UserResponse)
async def register(user: UserCreate, db: Session = Depends(get_db)):
    """Register a new user"""
    from datetime import datetime, timedelta
    
    logger = logging.getLogger(__name__)
    
    # Check if user already exists
    existing_user = get_user_by_email(db, user.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Create new user
    new_user = create_user(db, user)
    
    # Generate verification token
    verification_token = secrets.token_urlsafe(32)
    token_expires = datetime.utcnow() + timedelta(hours=24)
    
    # Update user with verification token
    new_user.email_verification_token = verification_token
    new_user.email_verification_token_expires = token_expires
    new_user.is_verified = False  # New users are not verified by default
    db.commit()
    
    # Send verification email
    try:
        await email_service.send_email_verification(new_user, verification_token)
        logger.info(f"Verification email sent to {new_user.email}")
    except Exception as e:
        logger.error(f"Failed to send verification email to {new_user.email}: {str(e)}")
        # Don't fail registration if email fails
    
    # Return user with verification message
    response = new_user.__dict__.copy()
    response['message'] = "¡Cuenta creada exitosamente! Te hemos enviado un email con un enlace de verificación. Revisa tu bandeja de entrada y haz clic en el enlace para activar tu cuenta."
    return response

@router.post("/login", response_model=Token)
async def login(user_credentials: UserLogin, db: Session = Depends(get_db)):
    """Login user and return access token"""
    
    # Get user by email
    user = get_user_by_email(db, user_credentials.email)
    
    if not user or not verify_password(user_credentials.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Account is disabled"
        )
    
    # Check if email is verified
    if not user.is_verified:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="¡Casi listo! Solo falta verificar tu email. Revisa tu bandeja de entrada y haz clic en el enlace de verificación que te enviamos. Si no lo encuentras, revisa tu carpeta de spam."
        )
    
    # Create access token
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    
    # Update last login
    update_user_last_login(db, user.id)
    
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/login/form", response_model=Token)
async def login_form(
    form_data: OAuth2PasswordRequestForm = Depends(), 
    db: Session = Depends(get_db)
):
    """Login using OAuth2 form (for OpenAPI docs)"""
    
    user_credentials = UserLogin(email=form_data.username, password=form_data.password)
    return await login(user_credentials, db)

@router.post("/password-reset/request", response_model=ResponseModel)
async def request_password_reset(
    reset_request: PasswordResetRequest, 
    db: Session = Depends(get_db)
):
    """Request password reset"""
    
    user = get_user_by_email(db, reset_request.email)
    if not user:
        # Don't reveal if email exists or not
        return ResponseModel(
            success=True,
            message="If the email exists, a reset link has been sent"
        )
    
    # Create reset token
    from app.core.security import create_reset_token
    reset_token = create_reset_token(user.email)
    
    # In production, send email with reset link
    # For now, we'll just return the token (for testing)
    # TODO: Implement email service
    
    return ResponseModel(
        success=True,
        message="Password reset link has been sent to your email",
        data={"reset_token": reset_token}  # Remove this in production
    )

@router.post("/password-reset/confirm", response_model=ResponseModel)
async def reset_password(
    reset_data: PasswordReset, 
    db: Session = Depends(get_db)
):
    """Reset password using token"""
    
    # Verify reset token
    try:
        email = verify_reset_token(reset_data.token)
    except HTTPException:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired reset token"
        )
    
    # Get user
    user = get_user_by_email(db, email)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Update password
    from app.services.user_service import update_user_password
    update_user_password(db, user.id, reset_data.new_password)
    
    return ResponseModel(
        success=True,
        message="Password has been reset successfully"
    )

@router.post("/verify-token", response_model=ResponseModel)
async def verify_token_endpoint(token: str, db: Session = Depends(get_db)):
    """Verify if a token is valid"""
    
    try:
        from app.core.security import verify_token
        payload = verify_token(token)
        email = payload.get("sub")
        
        if email:
            user = get_user_by_email(db, email)
            if user and user.is_active:
                return ResponseModel(
                    success=True,
                    message="Token is valid",
                    data={"email": email}
                )
        
        raise HTTPException(status_code=401, detail="Invalid token")
        
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )