#!/usr/bin/env python3
"""
Script para forzar que el frontend vea las mejoras inmediatamente
"""

import requests
import json
import sys
from pathlib import Path

# URL base del servidor
BASE_URL = "http://127.0.0.1:8000"

def create_admin_user():
    """Crear usuario admin para testing"""
    try:
        # Datos del admin
        admin_data = {
            "email": "admin@pdfextractor.com",
            "password": "admin123",
            "full_name": "Administrator"
        }
        
        # Intentar crear usuario
        response = requests.post(f"{BASE_URL}/api/auth/register", json=admin_data)
        if response.status_code == 201:
            print("✅ Usuario admin creado")
        elif response.status_code == 400 and "already registered" in response.text:
            print("✅ Usuario admin ya existe")
        else:
            print(f"⚠️  Respuesta de registro: {response.status_code}")
            
        # Login para obtener token
        login_data = {
            "username": admin_data["email"],
            "password": admin_data["password"]
        }
        
        login_response = requests.post(f"{BASE_URL}/api/auth/login", data=login_data)
        if login_response.status_code == 200:
            token_data = login_response.json()
            token = token_data.get("access_token")
            print(f"✅ Login exitoso, token obtenido")
            return token
        else:
            print(f"❌ Error en login: {login_response.status_code}")
            return None
            
    except Exception as e:
        print(f"❌ Error creando admin: {e}")
        return None

def upload_and_test_document(token):
    """Subir documento y probar las mejoras"""
    if not token:
        print("❌ No hay token disponible")
        return
    
    headers = {
        "Authorization": f"Bearer {token}"
    }
    
    # Ruta del PDF
    pdf_path = "/Users/leandrodebagge/code/pdf_reader/web_app/backend/uploads/document_ai/aeba7818-0e7a-4e89-938b-328061ead30b_NC 3051 CL 121 BOND.pdf"
    
    if not Path(pdf_path).exists():
        print(f"❌ PDF no encontrado: {pdf_path}")
        return
    
    try:
        # Subir documento
        print("📤 Subiendo documento...")
        with open(pdf_path, 'rb') as f:
            files = {'file': f}
            response = requests.post(f"{BASE_URL}/api/document-ai/upload", 
                                   headers=headers, files=files)
        
        if response.status_code == 200:
            doc_data = response.json()
            doc_id = doc_data.get("document_id")
            print(f"✅ Documento subido con ID: {doc_id}")
            
            # Obtener recomendaciones
            print("🔍 Obteniendo recomendaciones...")
            rec_response = requests.get(f"{BASE_URL}/api/document-ai/documents/{doc_id}/recommendations",
                                      headers=headers)
            
            if rec_response.status_code == 200:
                recommendations = rec_response.json()
                print("✅ Recomendaciones obtenidas:")
                if recommendations.get("success"):
                    doc_analysis = recommendations.get("document_analysis", {})
                    print(f"   📊 Tipo: {doc_analysis.get('document_type', 'unknown')}")
                    print(f"   📄 Páginas: {doc_analysis.get('total_pages', 0)}")
                    print(f"   📊 Tablas: {doc_analysis.get('has_tables', False)}")
                    
                    recs = recommendations.get("recommendations", {})
                    for format_name, rec in recs.items():
                        score = rec.get("quality_score", 0)
                        method = rec.get("recommended_method", "unknown")
                        print(f"   🎯 {format_name}: {score}/10 ({method})")
            
            # Probar exportación Word mejorada
            print("\n📄 Probando exportación Word mejorada...")
            export_data = {
                "document_id": doc_id,
                "format": "docx",
                "selection_ids": [],
                "custom_filename": "enhanced_test_word"
            }
            
            export_response = requests.post(f"{BASE_URL}/api/document-ai/export",
                                          headers={**headers, "Content-Type": "application/json"},
                                          json=export_data)
            
            if export_response.status_code == 200:
                export_result = export_response.json()
                print(f"✅ Word exportado: {export_result.get('filename')}")
                print(f"   📏 Tamaño: {export_result.get('file_size')} bytes")
            else:
                print(f"❌ Error exportando Word: {export_response.status_code}")
                print(f"   Detalles: {export_response.text}")
            
            # Probar exportación Excel mejorada
            print("\n📊 Probando exportación Excel mejorada...")
            export_data["format"] = "xlsx"
            export_data["custom_filename"] = "enhanced_test_excel"
            
            export_response = requests.post(f"{BASE_URL}/api/document-ai/export",
                                          headers={**headers, "Content-Type": "application/json"},
                                          json=export_data)
            
            if export_response.status_code == 200:
                export_result = export_response.json()
                print(f"✅ Excel exportado: {export_result.get('filename')}")
                print(f"   📏 Tamaño: {export_result.get('file_size')} bytes")
            else:
                print(f"❌ Error exportando Excel: {export_response.status_code}")
                print(f"   Detalles: {export_response.text}")
            
            print(f"\n🎉 ¡Mejoras activas! Ve a http://localhost:3000 y busca el documento ID {doc_id}")
            
        else:
            print(f"❌ Error subiendo documento: {response.status_code}")
            print(f"   Detalles: {response.text}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

def main():
    print("🚀 Forzando actualización del frontend con mejoras...")
    
    # Crear admin y obtener token
    token = create_admin_user()
    
    # Subir y probar documento
    upload_and_test_document(token)
    
    print("\n✅ Proceso completado!")
    print("🔄 Ahora ve al frontend y:")
    print("   1. Recarga la página")
    print("   2. Verás el documento procesado con mejoras")
    print("   3. Las exportaciones usarán los métodos mejorados")

if __name__ == "__main__":
    main()