# 🐋 Docker Deployment - PDF Reader Enterprise Platform

## 🎯 Sistema Completamente Containerizado

Este README te guiará para desplegar la **Plataforma Empresarial de Inteligencia Documental** completa usando Docker.

## 📋 Requisitos Previos

### Sistema Operativo
- **Linux, macOS o Windows** con WSL2
- **Docker Desktop** o Docker Engine + Docker Compose
- **Mínimo 8GB RAM** (recomendado 16GB para todas las funciones)
- **20GB espacio libre** en disco

### Software Requerido
```bash
# Verificar instalaciones
docker --version          # >= 20.0
docker-compose --version  # >= 2.0
```

## 🚀 Inicio Rápido

### 1. Preparación
```bash
# Navegar al directorio del proyecto
cd web_app

# Copiar configuración de ejemplo
cp .env.example .env

# Editar configuraciones (opcional para desarrollo)
nano .env
```

### 2. Inicio Automático
```bash
# Ejecutar script de inicio
./start.sh
```

### 3. Inicio Manual
```bash
# Construir contenedores
docker-compose build

# Iniciar todos los servicios
docker-compose up -d

# Ver logs
docker-compose logs -f
```

## 🏗️ Arquitectura de Contenedores

### Servicios Incluidos

| Servicio | Puerto | Descripción |
|----------|--------|-------------|
| **postgres** | 5432 | Base de datos PostgreSQL |
| **redis** | 6379 | Cache y cola de tareas |
| **minio** | 9000/9001 | Almacenamiento S3 compatible |
| **backend** | 8000 | API FastAPI principal |
| **frontend** | 3000 | Interfaz React |
| **celery_worker** | - | Procesamiento en background |
| **celery_beat** | - | Tareas programadas |

### Volúmenes Persistentes
- `postgres_data` - Datos de la base de datos
- `redis_data` - Cache de Redis
- `minio_data` - Almacenamiento de archivos
- `uploaded_files` - Archivos subidos por usuarios
- `data_platform` - Data warehouse
- `enterprise_logs` - Logs empresariales

## 🌐 URLs de Acceso

### Aplicación Principal
- **Frontend:** http://localhost:3000
- **Backend API:** http://localhost:8000
- **API Documentation:** http://localhost:8000/docs
- **OpenAPI Schema:** http://localhost:8000/redoc

### Servicios de Infraestructura
- **MinIO Console:** http://localhost:9001
  - Usuario: `minioadmin`
  - Contraseña: `minioadmin123`

### Health Checks
- **Backend Health:** http://localhost:8000/api/health
- **CORS Test:** http://localhost:8000/api/cors-test

## ⚙️ Configuración Avanzada

### Variables de Entorno Críticas

```bash
# Base de datos
DATABASE_URL=postgresql://pdf_user:pdf_password@postgres:5432/pdf_extractor

# Seguridad
SECRET_KEY=tu-clave-secreta-aqui
JWT_SECRET_KEY=tu-jwt-secret-aqui

# Funciones empresariales
ENABLE_ENTERPRISE_FEATURES=true
ENABLE_MULTI_TENANCY=true
ENABLE_ADVANCED_SECURITY=true

# APIs externas (opcional)
OPENAI_API_KEY=tu-openai-key
GOOGLE_API_KEY=tu-google-key
STRIPE_SECRET_KEY=tu-stripe-key
```

### Escalamiento de Recursos

Para entornos de producción, modifica `docker-compose.yml`:

```yaml
# Incrementar workers del backend
command: uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4

# Añadir límites de recursos
deploy:
  resources:
    limits:
      memory: 2G
      cpus: '1.0'
```

## 🛠️ Comandos Útiles

### Gestión de Contenedores
```bash
# Ver estado de servicios
docker-compose ps

# Ver logs de un servicio específico
docker-compose logs -f backend
docker-compose logs -f celery_worker

# Reiniciar un servicio
docker-compose restart backend

# Reconstruir y reiniciar
docker-compose up -d --build backend

# Parar todos los servicios
docker-compose down

# Parar y eliminar volúmenes (⚠️ BORRA TODOS LOS DATOS)
docker-compose down -v
```

### Debugging
```bash
# Acceder al contenedor del backend
docker-compose exec backend bash

# Ejecutar comandos en el backend
docker-compose exec backend python -c "print('Hello from container')"

# Ver variables de entorno
docker-compose exec backend env

# Verificar conexión a base de datos
docker-compose exec backend python -c "
from app.core.database import engine
print('DB Connection:', engine.url)
"
```

### Gestión de Base de Datos
```bash
# Acceder a PostgreSQL
docker-compose exec postgres psql -U pdf_user -d pdf_extractor

# Backup de base de datos
docker-compose exec postgres pg_dump -U pdf_user pdf_extractor > backup.sql

# Restaurar base de datos
docker-compose exec -T postgres psql -U pdf_user -d pdf_extractor < backup.sql
```

## 🔧 Solución de Problemas

### Problemas Comunes

#### 1. Error de construcción de contenedor
```bash
# Limpiar cache de Docker
docker system prune -a

# Reconstruir sin cache
docker-compose build --no-cache
```

#### 2. Puerto ya en uso
```bash
# Encontrar proceso usando el puerto
lsof -i :8000

# Cambiar puerto en docker-compose.yml
ports:
  - "8001:8000"  # Usar puerto 8001 en lugar de 8000
```

#### 3. Problemas de memoria
```bash
# Verificar uso de recursos
docker stats

# Incrementar memoria disponible para Docker Desktop
# Settings > Resources > Memory: 8GB mínimo
```

#### 4. Servicios no inician
```bash
# Verificar health checks
docker-compose ps

# Ver logs detallados
docker-compose logs --tail=100 service_name

# Reiniciar servicios dependientes
docker-compose restart postgres redis
```

### Logs de Diagnóstico
```bash
# Logs de todos los servicios
docker-compose logs

# Logs filtrados por nivel
docker-compose logs | grep ERROR
docker-compose logs | grep WARNING

# Logs en tiempo real
docker-compose logs -f --tail=50
```

## 🚀 Despliegue en Producción

### Consideraciones de Seguridad
```bash
# Cambiar credenciales por defecto en .env
SECRET_KEY=cryptographically-strong-secret-key
POSTGRES_PASSWORD=strong-database-password
MINIO_ROOT_PASSWORD=strong-minio-password

# Deshabilitar debug
DEBUG=false
ENVIRONMENT=production

# Configurar HTTPS
# Usar reverse proxy (nginx/traefik) con SSL
```

### Optimizaciones de Rendimiento
```bash
# Incrementar workers
WORKERS=4

# Configurar cache
REDIS_URL=redis://redis:6379/0

# Optimizar base de datos
# Configurar PostgreSQL para producción
```

### Monitoreo
```bash
# Agregar servicios de monitoreo
# - Prometheus + Grafana
# - ELK Stack para logs
# - Sentry para errores
```

## 📊 Funciones Empresariales Disponibles

### APIs Implementadas
- ✅ **250+ Endpoints** documentados
- ✅ **Inteligencia Multi-Formato** (PDF, Word, Excel)
- ✅ **IA Avanzada** y análisis predictivo
- ✅ **25+ Integraciones** empresariales
- ✅ **Multi-tenancy** completo
- ✅ **Seguridad empresarial** avanzada

### Dashboards Incluidos
- 📊 **Analytics** de documentos
- 🔒 **Security** y compliance
- 🔗 **Integrations** status
- 💼 **Enterprise** metrics

## 🆘 Soporte

### Logs de Sistema
Los logs se almacenan en:
- `enterprise_logs` volume
- Docker logs: `docker-compose logs`

### Configuración de Desarrollo
Para desarrollo, todos los archivos están montados como volúmenes, permitiendo hot-reload automático.

### Health Checks
El sistema incluye health checks automáticos para todos los servicios críticos.

---

## ✅ ¡Sistema Listo para Producción!

Una vez iniciado, tendrás acceso a una **Plataforma Empresarial de Inteligencia Documental** completa con todas las capacidades implementadas:

- 🏢 **Multi-tenancy** para organizaciones
- 🔗 **25+ Integraciones** CRM/ERP/DMS
- 🤖 **IA Avanzada** con análisis predictivo
- 🔒 **Seguridad empresarial** con compliance
- 📊 **Data Platform** con dashboards
- 🌐 **Conectores de ecosistema** (Google, Microsoft, AWS)

**¡Disfruta tu plataforma empresarial completa!** 🎉