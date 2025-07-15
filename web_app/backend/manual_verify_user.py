#!/usr/bin/env python3
"""
Script para verificar usuarios manualmente en desarrollo
"""

import sqlite3
import sys

def verify_user(email):
    """Verify a user manually by email"""
    try:
        conn = sqlite3.connect('pdf_extractor.db')
        cursor = conn.cursor()
        
        # Check if user exists
        cursor.execute('SELECT id, email, is_verified FROM users WHERE email = ?', (email,))
        user = cursor.fetchone()
        
        if not user:
            print(f"❌ Usuario con email '{email}' no encontrado")
            return False
        
        user_id, user_email, is_verified = user
        
        if is_verified:
            print(f"✅ Usuario '{email}' ya está verificado")
            return True
        
        # Verify the user
        cursor.execute('UPDATE users SET is_verified = 1 WHERE email = ?', (email,))
        conn.commit()
        
        print(f"✅ Usuario '{email}' verificado exitosamente")
        return True
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False
    finally:
        if conn:
            conn.close()

def list_unverified_users():
    """List all unverified users"""
    try:
        conn = sqlite3.connect('pdf_extractor.db')
        cursor = conn.cursor()
        
        cursor.execute('SELECT email, created_at FROM users WHERE is_verified = 0 ORDER BY created_at DESC')
        users = cursor.fetchall()
        
        if not users:
            print("✅ No hay usuarios sin verificar")
            return
        
        print("📋 Usuarios sin verificar:")
        for email, created_at in users:
            print(f"  - {email} (creado: {created_at})")
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso:")
        print("  python manual_verify_user.py <email>           # Verificar usuario específico")
        print("  python manual_verify_user.py --list            # Listar usuarios sin verificar")
        print()
        print("Ejemplos:")
        print("  python manual_verify_user.py test2@example.com")
        print("  python manual_verify_user.py --list")
        sys.exit(1)
    
    if sys.argv[1] == "--list":
        list_unverified_users()
    else:
        email = sys.argv[1]
        verify_user(email)