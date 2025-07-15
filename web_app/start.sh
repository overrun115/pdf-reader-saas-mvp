#!/bin/bash

echo "🚀 Iniciando PDF Reader Enterprise Platform..."

# Check if .env exists
if [ ! -f .env ]; then
    echo "📝 Creando archivo .env desde .env.example..."
    cp .env.example .env
    echo "⚠️  IMPORTANTE: Edita el archivo .env con tus configuraciones antes de continuar"
    echo "⚠️  Presiona Enter para continuar o Ctrl+C para salir y editar .env"
    read
fi

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker no está ejecutándose. Por favor inicia Docker Desktop."
    exit 1
fi

# Check if docker-compose is available
if ! command -v docker-compose > /dev/null 2>&1; then
    echo "❌ docker-compose no está instalado. Por favor instálalo."
    exit 1
fi

echo "🛠️  Construyendo contenedores (esto puede tomar varios minutos la primera vez)..."
docker-compose build

echo "🗄️  Iniciando servicios de base de datos..."
docker-compose up -d postgres redis minio

echo "⏳ Esperando a que los servicios estén listos..."
sleep 10

echo "🌐 Iniciando servicios de aplicación..."
docker-compose up -d backend celery_worker celery_beat

echo "⏳ Esperando a que el backend esté listo..."
sleep 15

echo "🎨 Iniciando frontend..."
docker-compose up -d frontend

echo ""
echo "✅ ¡Sistema iniciado exitosamente!"
echo ""
echo "📊 URLs disponibles:"
echo "   🖥️  Frontend: http://localhost:3000"
echo "   🔧 Backend API: http://localhost:8000"
echo "   📚 API Docs: http://localhost:8000/docs"
echo "   🗃️  MinIO Console: http://localhost:9001 (minioadmin/minioadmin123)"
echo ""
echo "🔍 Para ver logs:"
echo "   docker-compose logs -f backend"
echo "   docker-compose logs -f celery_worker"
echo ""
echo "🛑 Para detener:"
echo "   docker-compose down"
echo ""
echo "🔄 Para reiniciar:"
echo "   docker-compose restart"
echo ""

# Show status
echo "📊 Estado de los servicios:"
docker-compose ps