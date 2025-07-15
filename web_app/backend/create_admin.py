#!/usr/bin/env python3
"""
Script para crear usuario administrador
"""
import asyncio
import sys
from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.models.database import User, UserTier
from app.core.security import get_password_hash

async def create_admin_user():
    """Crear usuario administrador"""
    
    db: Session = SessionLocal()
    
    try:
        # Verificar si ya existe un admin
        admin_exists = db.query(User).filter(User.email == "admin@pdfextractor.com").first()
        
        if admin_exists:
            print("❌ Usuario admin ya existe: admin@pdfextractor.com")
            return
        
        # Crear usuario admin
        admin_user = User(
            email="admin@pdfextractor.com",
            hashed_password=get_password_hash("admin123"),
            full_name="Administrator",
            tier=UserTier.ENTERPRISE,
            subscription_active=True,
            files_processed_this_month=0,
            total_files_processed=0,
            is_active=True,
            is_verified=True
        )
        
        db.add(admin_user)
        db.commit()
        db.refresh(admin_user)
        
        print("✅ Usuario administrador creado exitosamente!")
        print(f"📧 Email: admin@pdfextractor.com")
        print(f"🔐 Password: admin123")
        print(f"🎯 Tier: {admin_user.tier.value}")
        print("\n🚀 Ahora puedes hacer login con estas credenciales en http://localhost:3000/login")
        
    except Exception as e:
        print(f"❌ Error creando usuario admin: {e}")
        db.rollback()
    
    finally:
        db.close()

if __name__ == "__main__":
    print("🔧 Creando usuario administrador...")
    asyncio.run(create_admin_user())