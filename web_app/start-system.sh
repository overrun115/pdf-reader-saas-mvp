#!/bin/bash

# Script para iniciar todo el sistema PDF Extractor con monitoreo automático
# Uso: ./start-system.sh

echo "🚀 Iniciando PDF Extractor System..."

# Verificar que Docker esté corriendo
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker no está corriendo. Por favor inicia Docker Desktop."
    exit 1
fi

# Iniciar servicios de Docker
echo "📦 Iniciando servicios Docker..."
docker-compose up -d

# Esperar a que los servicios estén listos
echo "⏳ Esperando a que los servicios inicien..."
sleep 10

# Verificar servicios
echo "🔍 Verificando servicios..."
if curl -s http://localhost:8000/health > /dev/null; then
    echo "✅ Backend está funcionando"
else
    echo "⚠️ Backend no responde, reiniciando..."
    docker-compose restart backend
    sleep 10
fi

if curl -s http://localhost:5432 > /dev/null 2>&1; then
    echo "✅ PostgreSQL está funcionando"
else
    echo "⚠️ PostgreSQL podría tener problemas"
fi

# Mostrar estado de servicios
echo -e "\n📊 Estado de servicios:"
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"

echo -e "\n🌐 URLs disponibles:"
echo "  Frontend: http://localhost:3000"
echo "  Backend:  http://localhost:8000"
echo "  API Docs: http://localhost:8000/docs"

echo -e "\n🔑 Credenciales:"
echo "  Email:    admin@pdfextractor.com"
echo "  Password: admin123"

echo -e "\n📋 Próximos pasos:"
echo "  1. Abre http://localhost:3000 en tu navegador"
echo "  2. En otra terminal, ejecuta: cd frontend && npm start"
echo "  3. En otra terminal, ejecuta: ./monitor-backend.sh"

echo -e "\n📝 Para ver logs:"
echo "  Backend:   docker logs web_app-backend-1 --tail 50"
echo "  Monitor:   tail -f backend-monitor.log"
echo "  Postgres:  docker logs web_app-postgres-1 --tail 20"

echo -e "\n✨ Sistema iniciado exitosamente!"