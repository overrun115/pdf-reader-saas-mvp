#!/usr/bin/env python3
"""
Script to verify existing users who were created before email verification was mandatory.
This helps with the migration to the new email verification system.
"""

import os
import sys
from datetime import datetime, timedelta
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

# Add the app directory to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def verify_existing_users():
    """Verify existing users who don't have verification tokens"""
    
    # Database connection
    DATABASE_URL = os.getenv('DATABASE_URL', 'postgresql://pdf_user:pdf_password@localhost:5432/pdf_extractor')
    engine = create_engine(DATABASE_URL)
    Session = sessionmaker(bind=engine)
    session = Session()
    
    try:
        # Find users who should be auto-verified (created more than 1 hour ago without verification token)
        cutoff_time = datetime.utcnow() - timedelta(hours=1)
        
        # Get users to verify
        result = session.execute(text("""
            SELECT id, email, created_at 
            FROM users 
            WHERE is_verified = false 
              AND created_at < :cutoff_time
              AND (email_verification_token IS NULL OR email_verification_token = '')
        """), {"cutoff_time": cutoff_time})
        
        users_to_verify = result.fetchall()
        
        if not users_to_verify:
            print("No users need to be auto-verified.")
            return
        
        print(f"Found {len(users_to_verify)} users to auto-verify:")
        for user in users_to_verify:
            print(f"  - {user.email} (ID: {user.id}, Created: {user.created_at})")
        
        # Ask for confirmation
        confirm = input("\nDo you want to verify these users? (y/N): ").lower()
        if confirm != 'y':
            print("Operation cancelled.")
            return
        
        # Verify the users
        session.execute(text("""
            UPDATE users 
            SET is_verified = true 
            WHERE is_verified = false 
              AND created_at < :cutoff_time
              AND (email_verification_token IS NULL OR email_verification_token = '')
        """), {"cutoff_time": cutoff_time})
        
        session.commit()
        print(f"Successfully verified {len(users_to_verify)} users.")
        
    except Exception as e:
        print(f"Error: {e}")
        session.rollback()
        return False
    finally:
        session.close()
    
    return True

def list_unverified_users():
    """List all unverified users"""
    
    # Database connection
    DATABASE_URL = os.getenv('DATABASE_URL', 'postgresql://pdf_user:pdf_password@localhost:5432/pdf_extractor')
    engine = create_engine(DATABASE_URL)
    Session = sessionmaker(bind=engine)
    session = Session()
    
    try:
        result = session.execute(text("""
            SELECT 
                id, 
                email, 
                is_verified, 
                email_verification_token IS NOT NULL as has_token,
                created_at 
            FROM users 
            WHERE is_verified = false
            ORDER BY created_at DESC
        """))
        
        unverified_users = result.fetchall()
        
        if not unverified_users:
            print("All users are verified.")
            return
        
        print(f"Unverified users ({len(unverified_users)}):")
        print("-" * 80)
        for user in unverified_users:
            token_status = "Has token" if user.has_token else "No token"
            print(f"ID: {user.id:3d} | {user.email:30s} | {token_status:10s} | {user.created_at}")
        
    except Exception as e:
        print(f"Error: {e}")
    finally:
        session.close()

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Manage user email verification')
    parser.add_argument('--list', action='store_true', help='List unverified users')
    parser.add_argument('--verify', action='store_true', help='Auto-verify existing users')
    
    args = parser.parse_args()
    
    if args.list:
        list_unverified_users()
    elif args.verify:
        verify_existing_users()
    else:
        print("Use --list to see unverified users or --verify to auto-verify existing users")
        print("Example: python verify_existing_users.py --list")