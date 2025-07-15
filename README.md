# 📊 PDF Extractor SaaS - Intelligent Table Extraction

Una plataforma SaaS completa para extraer tablas de archivos PDF usando inteligencia artificial con la librería Docling. Incluye sistema de suscripciones, pagos con Stripe, y gestión automática de usuarios.

## 🚀 Características Principales

### 🎯 **Funcionalidades Core**
- **Extracción Inteligente**: AI-powered table extraction usando Docling
- **Múltiples Formatos**: Exporta a CSV, Excel, JSON, HTML, TXT
- **Exportación Avanzada**: Preserva el layout original del PDF
- **Procesamiento Batch**: Maneja múltiples archivos simultáneamente
- **API REST**: Integración completa para desarrolladores
- **OCR Integrado**: Procesa documentos escaneados
- **Análisis de Layout**: Detecta columnas, tablas y estructura automáticamente

### 💳 **Sistema SaaS Completo**
- **Planes de Suscripción**: Free, Basic, Pro, Enterprise
- **Pagos con Stripe**: Checkout seguro y gestión de facturación
- **Límites por Tier**: Control automático de uso mensual
- **Portal de Facturación**: Gestión de suscripciones self-service

### 📧 **Comunicación Automatizada**
- **Emails de Bienvenida**: Onboarding automático
- **Confirmaciones de Pago**: Notificaciones de suscripciones
- **Advertencias de Uso**: Alertas antes de alcanzar límites
- **Templates Responsivos**: Emails HTML profesionales

### 🔐 **Gestión de Usuarios**
- **Autenticación JWT**: Login/registro seguro
- **Dashboard Personalizado**: Analytics y estadísticas de uso
- **Gestión de API Keys**: Para integraciones
- **Admin Panel**: Control total del sistema

## 📊 **Formatos de Exportación**

### **Formatos Disponibles**
- **TXT**: Texto plano con preservación de espaciado y estructura
- **HTML**: Formato web con CSS para mantener layout original
- **JSON**: Datos estructurados con metadatos completos
- **CSV**: Tablas extraídas en formato de hoja de cálculo
- **XLSX**: Excel con múltiples hojas, formato y tablas estructuradas

### **Características de Exportación**
- **Preservación de Layout**: Mantiene la disposición visual original
- **Detección de Columnas**: Identifica automáticamente layouts multi-columna
- **Análisis de Tablas**: Extrae tablas complejas con estructura
- **Headers Jerárquicos**: Preserva títulos y subtítulos con formato
- **Espaciado Inteligente**: Mantiene alineación y espaciado original

## 🏗️ Arquitectura

### **Backend (FastAPI + PostgreSQL)**
- API REST escalable con documentación automática
- Base de datos robusta con modelos relacionales
- Sistema de webhooks para eventos de Stripe
- Procesamiento asíncrono con Celery + Redis

### **Frontend (React + TypeScript + Material-UI)**
- Interfaz moderna y responsiva
- Gestión de estado con Zustand
- Tema oscuro/claro dinámico
- Componentes reutilizables

## 📋 Planes de Suscripción

| Plan | Archivos/Mes | Precio | Características |
|------|--------------|---------|-----------------|
| **Free** | 5 | $0 | Extracción básica, CSV/TXT export |
| **Basic** | 50 | $9.99 | Extracción avanzada, CSV/Excel/HTML/JSON, API |
| **Pro** | 200 | $29.99 | Extracción premium, Layout preservation, Batch processing |
| **Enterprise** | Ilimitado | $99.99 | Todo incluido, Soporte dedicado, Integraciones custom |

## ⚙️ Requisitos del Sistema

### **Backend Requirements**
- Python 3.9+
- PostgreSQL
- Redis (para Celery)
- SendGrid API Key (emails)
- Stripe Account (pagos)

### **Frontend Requirements**
- Node.js 16+
- npm o yarn


## 🔧 Configuración e Instalación

### 1. **Configuración de Variables de Entorno**

Crea un archivo `.env` en el directorio del backend:

```bash
cd web_app/backend
touch .env
```

Agrega las siguientes variables:

```env
# Base de Datos
DATABASE_URL=postgresql://user:password@localhost/pdf_extractor

# Stripe (Pagos)
STRIPE_SECRET_KEY=sk_test_your_stripe_secret_key
STRIPE_PUBLISHABLE_KEY=pk_test_your_stripe_publishable_key
STRIPE_WEBHOOK_SECRET=whsec_your_webhook_secret
STRIPE_PRICE_BASIC=price_your_basic_price_id
STRIPE_PRICE_PRO=price_your_pro_price_id
STRIPE_PRICE_ENTERPRISE=price_your_enterprise_price_id

# SendGrid (Emails)
SENDGRID_API_KEY=SG.your_sendgrid_api_key
FROM_EMAIL=noreply@yourcompany.com
FROM_NAME=PDF Extractor

# App Configuration
SECRET_KEY=your_secret_key_here
FRONTEND_URL=http://localhost:3500
ENVIRONMENT=development
```

### 2. **Instalación del Backend**

```bash
cd web_app/backend

# Crear entorno virtual
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate

# Instalar dependencias
pip install -r requirements.txt

# Ejecutar migraciones de base de datos
alembic upgrade head

# Crear usuario administrador
python create_admin.py

# Iniciar servidor
python -m app.main
```

### 3. **Instalación del Frontend**

```bash
cd web_app/frontend

# Instalar dependencias
npm install

# Iniciar servidor de desarrollo
npm start
```

### 4. **Configuración de Stripe**

1. **Crear Cuenta en Stripe**:
   - Regístrate en [stripe.com](https://stripe.com)
   - Obtén tus API keys desde el dashboard

2. **Crear Productos y Precios**:
   ```bash
   # Desde el dashboard de Stripe, crea productos para:
   # - Basic Plan ($9.99/mes)
   # - Pro Plan ($29.99/mes) 
   # - Enterprise Plan ($99.99/mes)
   ```

3. **Configurar Webhooks**:
   - URL: `http://localhost:9700/api/webhooks/stripe`
   - Eventos: `customer.subscription.*`, `invoice.payment_*`, `checkout.session.completed`

### 5. **Configuración de SendGrid**

1. **Crear Cuenta en SendGrid**:
   - Regístrate en [sendgrid.com](https://sendgrid.com)
   - Genera una API key

2. **Verificar Dominio** (Opcional):
   - Para emails de producción, verifica tu dominio

## 🚀 Ejecución del Sistema

### **Modo Desarrollo**

```bash
# Terminal 1 - Backend
cd web_app/backend
source venv/bin/activate
python -m app.main

# Terminal 2 - Frontend
cd web_app/frontend
npm start
```

### **URLs de Acceso**

- **🌐 Aplicación**: http://localhost:3500
- **🔧 API Backend**: http://localhost:9700
- **📚 API Docs**: http://localhost:9700/docs
- **❤️ Health Check**: http://localhost:9700/health

### **Credenciales de Administrador**

```
Email: admin@pdfextractor.com
Password: admin123
```

## 🧪 Testing

### **Backend Tests**
```bash
cd web_app/backend
pytest
```

### **Frontend Tests**
```bash
cd web_app/frontend
npm test
```

## 📊 Monitoreo y Analytics

### **Métricas Disponibles**
- Usuarios activos por tier
- Archivos procesados por día/mes
- Ingresos por plan de suscripción
- Tasas de conversión de planes
- Uso de API por usuario

### **Logs del Sistema**
```bash
# Backend logs
tail -f web_app/backend/app.log

# Stripe webhook logs
tail -f web_app/backend/stripe_webhooks.log
```

## 🔒 Seguridad

- **Autenticación JWT** con tokens de corta duración
- **Validación de entrada** en todos los endpoints
- **Rate limiting** por usuario y plan
- **Webhooks verificados** con signatures de Stripe
- **Variables de entorno** para secretos

## 🚀 Despliegue en Producción

### **Variables de Entorno de Producción**
```env
ENVIRONMENT=production
DATABASE_URL=postgresql://user:pass@prod-db/database
STRIPE_SECRET_KEY=sk_live_your_live_key
SENDGRID_API_KEY=SG.your_production_key
FRONTEND_URL=https://yourapp.com
```

### **Servicios Recomendados**
- **Backend**: Heroku, DigitalOcean, AWS
- **Base de Datos**: PostgreSQL (RDS, DigitalOcean Databases)
- **Frontend**: Vercel, Netlify, Cloudflare Pages
- **Redis**: Redis Cloud, AWS ElastiCache

## 📞 Soporte

Para soporte técnico o comercial:
- 📧 Email: admin@pdfextractor.com
- 📚 Documentación: http://localhost:9700/docs
- 🐛 Issues: GitHub Issues

---

**¡Tu plataforma SaaS de extracción de tablas está lista para generar ingresos!** 💰




## 👨‍💼 Panel de Administración

### **Acceso al Panel Admin**

El sistema incluye un panel de administración completo para gestionar el negocio y controlar las operaciones.

**Credenciales de Administrador:**
```
Email: admin@pdfextractor.com  
Password: admin123
```

**URL de Acceso:** http://localhost:3500/admin

### **Funcionalidades del Admin Panel**

#### 🎯 **Overview Dashboard**
- **Métricas Principales**: Usuarios totales, suscripciones activas, archivos procesados
- **MRR/ARR**: Ingresos recurrentes mensuales y anuales
- **Gráficos de Crecimiento**: Tendencias de usuarios y procesamiento (últimos 30 días)
- **Distribución por Tier**: Análisis visual de usuarios por plan
- **Actividad Reciente**: Archivos procesados y nuevos usuarios

#### 💰 **Revenue Analytics**
- **Métricas de Ingresos**: MRR, ARR, suscripciones activas
- **Ingresos por Tier**: Análisis detallado de revenue por plan
- **Nuevas Suscripciones**: Tracking de conversiones en 30 días
- **Gráficos de Revenue**: Visualización de ingresos por plan

#### 👥 **User Management**
- **Lista Completa de Usuarios**: Tabla paginada con todos los usuarios
- **Filtros Avanzados**: Búsqueda por email, filtro por tier
- **Gestión de Tiers**: Cambio manual de planes de usuario
- **Métricas por Usuario**: Archivos procesados, actividad, fecha de registro
- **Estadísticas de Revenue**: Cálculo automático de ingresos por usuario

#### 🔧 **System Health**
- **Estado de Base de Datos**: Monitoreo de conexión y tablas

- **Procesamiento de Archivos**: Archivos fallidos en 24h
- **Cola de Procesamiento**: Estado del sistema de procesamiento
- **Uptime del Sistema**: Monitoreo de disponibilidad

### **Características Técnicas**

- **Autenticación Protegida**: Solo usuarios admin pueden acceder
- **Datos en Tiempo Real**: Métricas actualizadas dinámicamente
- **Interfaz Responsive**: Optimizada para desktop y móvil
- **Gráficos Interactivos**: Powered by Recharts
- **Acciones Administrativas**: Cambio de tiers, gestión de usuarios

---

## 🧪 Pruebas de Stripe

### **Tarjetas de Prueba**

Para probar los pagos usa estas tarjetas de Stripe:

**Tarjeta que funciona siempre:**
```
Número: 4242 4242 4242 4242
Fecha: 12/25 (cualquier fecha futura)
CVC: 123 (cualquier 3 dígitos)
Código postal: 12345
Nombre: Cualquier nombre
```

**Otras tarjetas útiles:**
- **Tarjeta declinada**: 4000 0000 0000 0002
- **Fondos insuficientes**: 4000 0000 0000 9995  
- **Requiere autenticación**: 4000 0000 0000 3220

### **Proceso de Prueba**

1. ✅ **Completar Pago**: Usar tarjeta 4242 4242 4242 4242
2. ✅ **Redirección**: Página de éxito automática
3. ✅ **Actualización de Plan**: Ver nuevo tier en /subscription
4. ✅ **Acceso Premium**: Funciones desbloqueadas según el plan

---

## 📊 Gestión y Monitoreo

### **1. Panel de Stripe**

**Dashboard:** https://dashboard.stripe.com/

**Funcionalidades:**
- 💳 Ver transacciones y suscripciones activas/canceladas
- 👥 Gestionar clientes y cambiar planes  
- 📈 Analizar MRR y reportes de ventas
- 🔗 Configurar webhooks para notificaciones
- 🛍️ Gestionar productos y precios

### **2. Base de Datos PostgreSQL**

**Acceso directo:**
```bash
docker-compose exec postgres psql -U pdf_user -d pdf_extractor
```

**Consultas útiles:**
```sql
-- Ver todos los usuarios
SELECT email, tier, subscription_active, files_processed_this_month FROM users;

-- Ver usuarios premium  
SELECT email, tier, subscription_id FROM users WHERE tier != 'free';

-- Análisis de uso por tier
SELECT tier, COUNT(*) as users, AVG(files_processed_this_month) as avg_usage 
FROM users GROUP BY tier;

-- Revenue analysis
SELECT tier, COUNT(*) as users,
  CASE tier 
    WHEN 'basic' THEN COUNT(*) * 9.99
    WHEN 'pro' THEN COUNT(*) * 29.99  
    WHEN 'enterprise' THEN COUNT(*) * 99.99
    ELSE 0 
  END as monthly_revenue
FROM users WHERE subscription_active = true GROUP BY tier;
```

### **3. Logs y Diagnóstico**

**Logs del backend:**
```bash
docker-compose logs backend | grep ERROR
docker-compose logs backend | grep "File processed"
```

**Monitoreo de webhooks:**
```bash
docker-compose logs backend | grep "Stripe webhook"
```

**Verificar procesamiento:**
```bash
docker-compose logs backend | grep "Table extraction"
```



