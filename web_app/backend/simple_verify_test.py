#!/usr/bin/env python3
"""
Simple verification test using FastAPI dependencies directly
"""

import sys
import os
sys.path.append(os.path.dirname(__file__))

from app.core.database import SessionLocal
from app.models.database import User
from datetime import datetime
from pydantic import BaseModel

class VerifyEmailRequest(BaseModel):
    token: str

def test_verify_logic(token: str):
    """Test the verification logic directly"""
    db = SessionLocal()
    try:
        print(f"Testing token: {token[:20]}...")
        
        # Find user by verification token
        user = db.query(User).filter(
            User.email_verification_token == token
        ).first()
        
        print(f"User found: {user is not None}")
        if user:
            print(f"User email: {user.email}")
            print(f"User verified: {user.is_verified}")
            print(f"Token expires: {user.email_verification_token_expires}")
            
            # Check if already verified
            if user.is_verified:
                print("✅ Email is already verified!")
                return True
            
            # Check expiration
            if user.email_verification_token_expires:
                if isinstance(user.email_verification_token_expires, str):
                    try:
                        expires_dt = datetime.fromisoformat(user.email_verification_token_expires.replace('Z', '+00:00') if user.email_verification_token_expires.endswith('Z') else user.email_verification_token_expires)
                    except ValueError:
                        expires_dt = datetime.strptime(user.email_verification_token_expires, '%Y-%m-%d %H:%M:%S.%f')
                else:
                    expires_dt = user.email_verification_token_expires
                
                print(f"Expires: {expires_dt}")
                print(f"Now: {datetime.utcnow()}")
                print(f"Valid: {expires_dt > datetime.utcnow()}")
                
                if expires_dt <= datetime.utcnow():
                    print("❌ Token has expired")
                    return False
            
            # Verify user
            user.is_verified = True
            user.email_verification_token = None
            user.email_verification_token_expires = None
            db.commit()
            
            print("✅ User verified successfully!")
            return True
        else:
            print("❌ User not found")
            return False
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        db.close()

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python simple_verify_test.py <token>")
        sys.exit(1)
    
    token = sys.argv[1]
    test_verify_logic(token)