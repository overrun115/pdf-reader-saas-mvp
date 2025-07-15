# 📊 PDF Table Extractor SaaS

Una aplicación web SaaS moderna para extraer tablas de archivos PDF con mapeo inteligente de columnas y IA. **10x más barata que los competidores** con funcionalidades únicas que ninguna otra solución ofrece.

## 🚀 Características Principales

### 🤖 **Funcionalidades Únicas (NINGÚN competidor las tiene)**

- **✨ Mapeo Inteligente de Columnas**: Detecta automáticamente cuando las columnas son números (1, 2, 3) y las mapea a nombres descriptivos de tablas anteriores
- **🔍 Preview con Sugerencias ML**: Vista previa de tablas con recomendaciones inteligentes antes del procesamiento
- **🔄 Procesamiento Colaborativo**: Comparte resultados, historial versionado, comentarios en tablas
- **⚡ Batch Processing Inteligente**: Procesa múltiples PDFs simultáneamente con deduplicación automática
- **🎯 API-First con Webhooks**: Arquitectura completa de API REST con notificaciones en tiempo real

### 💰 **Pricing Disruptivo**

| **Nuestro Plan** | **Precio** | **Competidor** | **Ahorro** |
|------------------|------------|----------------|------------|
| **Gratis** | 5 PDFs/mes | Tabula (solo local) | 100% |
| **Básico** | $9/mes | Docsumo $500/mes | **98%** |
| **Pro** | $29/mes | Textract ~$45/mes | **35%** |
| **Enterprise** | $99/mes | Docsumo $1000+/mes | **90%** |

### 🎯 **Tecnología Superior**

- **Backend**: FastAPI + PostgreSQL + Redis + Celery
- **Frontend**: React + TypeScript + Material-UI
- **Procesamiento**: Docling + Pandas + ML
- **Arquitectura**: Microservicios escalables con Docker

## 📁 Estructura del Proyecto

```
web_app/
├── backend/                 # FastAPI Backend
│   ├── app/
│   │   ├── api/            # Endpoints REST
│   │   ├── core/           # Configuración y seguridad
│   │   ├── models/         # Modelos de base de datos
│   │   ├── services/       # Lógica de negocio
│   │   ├── tasks/          # Trabajos en background (Celery)
│   │   └── main.py         # Aplicación principal
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/               # React Frontend
│   ├── src/
│   │   ├── components/     # Componentes reutilizables
│   │   ├── pages/          # Páginas de la aplicación
│   │   ├── services/       # Servicios API
│   │   ├── store/          # Estado global (Zustand)
│   │   └── App.tsx
│   ├── package.json
│   └── Dockerfile
├── shared/                 # Lógica compartida
│   └── pdf_extractor.py   # Core de extracción PDF
└── docker-compose.yml     # Orquestación completa
```

## 🛠️ Instalación y Configuración

### **Prerequisitos**

- Docker y Docker Compose
- Git
- Node.js 18+ (para desarrollo local)
- Python 3.11+ (para desarrollo local)

### **🚀 Inicio Rápido (Recomendado)**

1. **Clonar el repositorio**
   ```bash
   git clone <repository-url>
   cd pdf_reader/web_app
   ```

2. **Iniciar toda la aplicación con Docker**
   ```bash
   docker-compose up --build
   ```

3. **Acceder a la aplicación**
   - **Frontend**: http://localhost:3000
   - **Backend API**: http://localhost:8000
   - **Documentación API**: http://localhost:8000/docs

### **⚙️ Variables de Entorno**

Crear un archivo `.env` en la raíz:

```env
# Base de datos
DATABASE_URL=postgresql://pdf_user:pdf_password@postgres:5432/pdf_extractor

# Redis
REDIS_URL=redis://redis:6379/0

# Seguridad
SECRET_KEY=your-super-secret-key-change-in-production

# API
REACT_APP_API_URL=http://localhost:8000

# Configuración de archivos
MAX_FILE_SIZE=52428800  # 50MB
UPLOAD_DIR=uploads

# Límites por tier
FREE_TIER_LIMIT=5
BASIC_TIER_LIMIT=50
PRO_TIER_LIMIT=200
ENTERPRISE_TIER_LIMIT=-1

# Email (opcional)
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password

# Stripe (para pagos)
STRIPE_SECRET_KEY=sk_test_...
STRIPE_WEBHOOK_SECRET=whsec_...
```

## 📖 Guía de Uso

### **🔐 Autenticación**

1. **Registro**: Crear cuenta gratuita (5 PDFs/mes)
2. **Login**: Email y contraseña
3. **API Keys**: Generar claves para integración (Plan Pro+)

### **📤 Subir y Procesar PDFs**

1. **Upload**: Arrastra archivos PDF o usa el botón de selección
2. **Preview**: Ve las tablas detectadas antes de procesar
3. **Configure**: Elige formato de salida (Excel, CSV, ambos)
4. **Process**: Extracción con mapeo inteligente de columnas
5. **Download**: Descarga los resultados procesados

### **🔍 Funcionalidades Avanzadas**

#### **Mapeo Inteligente de Columnas**
```python
# Ejemplo: PDF con tablas inconsistentes
Tabla 1: ["Nombre", "Edad", "Ciudad"]
Tabla 2: ["1", "2", "3"]  # ← Automáticamente mapeado a ["Nombre", "Edad", "Ciudad"]
```

#### **Preview con Sugerencias ML**
- Detecta complejidad del documento
- Recomienda formato óptimo
- Estima tiempo de procesamiento
- Sugiere configuraciones

#### **API REST Completa**
```bash
# Subir archivo
curl -X POST "http://localhost:8000/api/files/upload" \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -F "file=@document.pdf"

# Procesar
curl -X POST "http://localhost:8000/api/files/123/process" \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -d '{"output_format": "excel"}'
```

### **📊 Dashboard y Analytics**

- Estadísticas de uso en tiempo real
- Historial de archivos procesados
- Métricas de rendimiento
- Límites por plan

## 🏗️ Desarrollo

### **Backend Development**

```bash
cd backend

# Instalar dependencias
pip install -r requirements.txt

# Configurar base de datos
alembic upgrade head

# Ejecutar servidor de desarrollo
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Ejecutar worker Celery
celery -A app.tasks.celery worker --loglevel=info
```

### **Frontend Development**

```bash
cd frontend

# Instalar dependencias
npm install

# Ejecutar servidor de desarrollo
npm start

# Build para producción
npm run build
```

### **🧪 Testing**

```bash
# Backend tests
cd backend
pytest

# Frontend tests
cd frontend
npm test

# Integration tests
docker-compose -f docker-compose.test.yml up --build
```

## 🚀 Deployment

### **🐳 Docker Production**

```bash
# Build images
docker-compose -f docker-compose.prod.yml build

# Deploy
docker-compose -f docker-compose.prod.yml up -d

# Monitor logs
docker-compose logs -f
```

### **☁️ Cloud Deployment**

#### **AWS ECS / Fargate**
```bash
# Push to ECR
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin <account>.dkr.ecr.us-east-1.amazonaws.com

docker tag pdf-extractor-backend:latest <account>.dkr.ecr.us-east-1.amazonaws.com/pdf-extractor:backend
docker push <account>.dkr.ecr.us-east-1.amazonaws.com/pdf-extractor:backend
```

#### **Google Cloud Run**
```bash
# Build and deploy
gcloud builds submit --tag gcr.io/PROJECT_ID/pdf-extractor-backend
gcloud run deploy --image gcr.io/PROJECT_ID/pdf-extractor-backend --platform managed
```

#### **DigitalOcean App Platform**
```yaml
# app.yaml
name: pdf-extractor
services:
- name: backend
  source_dir: /backend
  github:
    repo: your-repo
    branch: main
  run_command: uvicorn app.main:app --host 0.0.0.0 --port 8080
  environment_slug: python
  instance_count: 1
  instance_size_slug: basic-xxs
```

## 📊 API Documentation

### **🔑 Authentication**
```bash
Authorization: Bearer YOUR_API_KEY
```

### **📋 Main Endpoints**

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| `POST` | `/api/files/upload` | Subir PDF |
| `GET` | `/api/files/{id}/preview` | Preview de tablas |
| `POST` | `/api/files/{id}/process` | Procesar archivo |
| `GET` | `/api/files/{id}/status` | Estado del procesamiento |
| `GET` | `/api/files/{id}/download` | Descargar resultado |

### **🎯 Webhook Events**
```json
{
  "event": "processing.completed",
  "file_id": 123,
  "status": "completed",
  "tables_found": 3,
  "download_url": "https://api.pdfextractor.com/files/123/download"
}
```

## 🔧 Configuración Avanzada

### **🔄 Procesamiento Asíncrono**

```python
# Configurar Celery para alta carga
CELERY_WORKER_CONCURRENCY = 4
CELERY_MAX_TASKS_PER_CHILD = 100
CELERY_TASK_SOFT_TIME_LIMIT = 300
```

### **📈 Monitoreo**

```bash
# Métricas con Prometheus
docker run -d -p 9090:9090 prom/prometheus

# Logs estructurados
tail -f logs/app.log | jq '.'

# Health checks
curl http://localhost:8000/health
```

### **🛡️ Seguridad**

- Validación estricta de archivos PDF
- Rate limiting por IP y usuario
- Encriptación de datos en tránsito
- Limpieza automática de archivos (30 días)
- API keys con expiración

## 📈 Escalabilidad

### **🏗️ Arquitectura de Producción**

```
Load Balancer (Nginx)
    ↓
Frontend (React) → CDN
    ↓
API Gateway
    ↓
Backend Services (FastAPI)
    ↓
Message Queue (Redis/Celery)
    ↓
Workers (PDF Processing)
    ↓
Database (PostgreSQL)
    ↓
File Storage (S3/MinIO)
```

### **⚡ Optimizaciones**

- **Caching**: Redis para sesiones y resultados
- **CDN**: CloudFlare para archivos estáticos
- **Database**: Índices optimizados y connection pooling
- **Processing**: Queue prioritizada por tier de usuario
- **Monitoring**: Grafana + Prometheus

## 🐛 Troubleshooting

### **❗ Problemas Comunes**

#### **Docker no inicia**
```bash
# Limpiar containers
docker-compose down -v
docker system prune -a

# Rebuilder
docker-compose up --build
```

#### **Error de permisos en uploads**
```bash
# Crear directorio con permisos
mkdir -p uploads
chmod 755 uploads
```

#### **Base de datos no conecta**
```bash
# Verificar servicio PostgreSQL
docker-compose ps postgres
docker-compose logs postgres

# Reset database
docker-compose down -v
docker-compose up postgres -d
```

#### **Celery worker no procesa**
```bash
# Verificar Redis
docker-compose logs redis

# Restart worker
docker-compose restart celery_worker
```

### **🔍 Debug Mode**

```bash
# Backend debug
DEBUG=True uvicorn app.main:app --reload

# Frontend debug
REACT_APP_DEBUG=true npm start

# Docker debug
docker-compose -f docker-compose.debug.yml up
```

## 📞 Soporte

### **📋 Antes de reportar un issue**

1. Verificar que Docker esté corriendo
2. Revisar logs: `docker-compose logs`
3. Verificar variables de entorno
4. Probar con un PDF simple primero

### **🆘 Obtener Ayuda**

- **Issues**: GitHub Issues para bugs
- **Email**: support@pdfextractor.com
- **Discord**: Comunidad de desarrolladores
- **Docs**: Documentación completa en `/docs`

## 🎯 Roadmap

### **📅 Q1 2024**
- ✅ MVP con funcionalidades core
- ✅ API REST completa
- ✅ Dashboard de usuario
- 🔄 Pagos con Stripe

### **📅 Q2 2024**
- 🔄 Colaboración en tiempo real
- 📋 Marketplace de templates
- 📋 Integración con Zapier
- 📋 Mobile app (React Native)

### **📅 Q3 2024**
- 📋 AI avanzado para detección de datos
- 📋 White-label solutions
- 📋 Enterprise on-premise
- 📋 Analytics avanzados

## 📄 Licencia

MIT License - Ver archivo [LICENSE](LICENSE) para detalles.

## 🙏 Contribuciones

Las contribuciones son bienvenidas! Ver [CONTRIBUTING.md](CONTRIBUTING.md) para detalles.

## ⭐ Agradecimientos

- **Docling**: Biblioteca de extracción PDF
- **FastAPI**: Framework web moderno
- **React**: Biblioteca de UI
- **Material-UI**: Componentes de diseño
- **PostgreSQL**: Base de datos robusta

---

## 🎉 ¡Comienza Ahora!

```bash
git clone <repository-url>
cd pdf_reader/web_app
docker-compose up --build
```

Visita http://localhost:3000 y comienza a extraer tablas de PDFs con IA! 🚀

---

**Desarrollado con ❤️ para hacer la extracción de tablas PDF 10x más fácil y barata.**