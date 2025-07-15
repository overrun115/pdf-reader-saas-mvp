#!/usr/bin/env python3
"""
Check database configuration
"""

import os
import sys
sys.path.append(os.path.dirname(__file__))

from app.core.config import settings

print("=== Database Configuration ===")
print(f"DATABASE_URL from settings: {settings.DATABASE_URL}")
print(f"DATABASE_URL from env: {os.getenv('DATABASE_URL', 'Not set')}")
print(f"Environment: {settings.ENVIRONMENT}")
print(f"Debug: {settings.DEBUG}")

# Check if .env file exists
env_file_path = os.path.join(os.path.dirname(__file__), '.env')
print(f"\n.env file exists: {os.path.exists(env_file_path)}")

if os.path.exists(env_file_path):
    print("Content of .env file (DATABASE_URL line):")
    with open(env_file_path, 'r') as f:
        for line_num, line in enumerate(f, 1):
            if 'DATABASE_URL' in line:
                print(f"  Line {line_num}: {line.strip()}")

# Try to connect to database
try:
    from app.core.database import engine
    print(f"\nDatabase engine URL: {engine.url}")
    print(f"Database driver: {engine.dialect.name}")
    
    # Try to execute a simple query
    from sqlalchemy import text
    with engine.connect() as conn:
        result = conn.execute(text("SELECT 1 as test"))
        print("✅ Database connection successful")
        
        # Check if users table exists
        try:
            result = conn.execute(text("SELECT COUNT(*) FROM users"))
            count = result.scalar()
            print(f"✅ Users table exists with {count} records")
            
            # Check for verification tokens
            result = conn.execute(text("SELECT COUNT(*) FROM users WHERE email_verification_token IS NOT NULL"))
            token_count = result.scalar()
            print(f"✅ Users with verification tokens: {token_count}")
            
            # Show some sample users
            result = conn.execute(text("SELECT email, is_verified, email_verification_token FROM users WHERE email_verification_token IS NOT NULL LIMIT 3"))
            users = result.fetchall()
            print("Sample users with tokens:")
            for user in users:
                token_preview = user[2][:20] + "..." if user[2] else "None"
                print(f"  - {user[0]}: verified={user[1]}, token={token_preview}")
                
        except Exception as e:
            print(f"❌ Users table issue: {str(e)}")
            
except Exception as e:
    print(f"❌ Database connection failed: {str(e)}")