# 🔧 Documentación para Desarrolladores

## 📁 Estructura del Proyecto

```
pdf_reader/
├── web_app/
│   ├── backend/                 # FastAPI Backend
│   │   ├── app/
│   │   │   ├── api/            # Endpoints API
│   │   │   │   ├── routes/     # Rutas principales
│   │   │   │   ├── subscription.py  # Endpoints de suscripciones
│   │   │   │   └── webhooks.py      # Webhooks de Stripe
│   │   │   ├── core/           # Configuración central
│   │   │   ├── models/         # Modelos de datos
│   │   │   ├── services/       # Lógica de negocio
│   │   │   │   ├── stripe_service.py   # Integración Stripe
│   │   │   │   ├── email_service.py    # Sistema de emails
│   │   │   │   └── file_service.py     # Procesamiento archivos
│   │   │   └── templates/      # Templates de email
│   │   └── requirements.txt    # Dependencias Python
│   └── frontend/               # React Frontend
│       ├── src/
│       │   ├── components/     # Componentes reutilizables
│       │   │   └── Subscription/      # Componentes de suscripción
│       │   ├── pages/          # Páginas principales
│       │   │   └── Subscription/      # Páginas de suscripción
│       │   ├── services/       # APIs y servicios
│       │   │   └── subscriptionApi.ts # API de suscripciones
│       │   └── store/          # Estado global
│       └── package.json        # Dependencias Node.js
```

## 🔌 APIs Implementadas

### **Endpoints de Suscripción**

#### `GET /api/subscription/plans`
Obtiene todos los planes de suscripción disponibles.

**Response:**
```json
[
  {
    "tier": "basic",
    "name": "Basic Plan",
    "price": 9.99,
    "price_id": "price_stripe_id",
    "features": ["50 files per month", "API access"],
    "files_per_month": 50
  }
]
```

#### `POST /api/subscription/create-checkout`
Crea una sesión de checkout de Stripe.

**Request:**
```json
{
  "price_id": "price_stripe_id",
  "success_url": "http://localhost:3500/subscription/success",
  "cancel_url": "http://localhost:3500/subscription"
}
```

#### `GET /api/subscription/status`
Obtiene el estado actual de la suscripción del usuario.

#### `POST /api/subscription/create-billing-portal`
Crea una sesión del portal de facturación de Stripe.

### **Webhooks de Stripe**

#### `POST /api/webhooks/stripe`
Maneja todos los eventos de webhooks de Stripe:

- `customer.subscription.created` - Nueva suscripción
- `customer.subscription.updated` - Actualización de suscripción
- `customer.subscription.deleted` - Cancelación de suscripción
- `invoice.payment_succeeded` - Pago exitoso
- `invoice.payment_failed` - Pago fallido
- `checkout.session.completed` - Checkout completado

## 📧 Sistema de Emails

### **Templates Disponibles**

1. **Welcome Email** (`welcome.html`)
   - Enviado cuando se registra un nuevo usuario
   - Incluye información del plan y links útiles

2. **Subscription Confirmation** (`subscription_confirmation.html`)
   - Enviado cuando se confirma una nueva suscripción
   - Detalles del plan y próximos pasos

3. **Usage Warning** (`usage_warning.html`)
   - Enviado cuando el usuario está cerca del límite (80% y 95%)
   - Incluye estadísticas de uso y opciones de upgrade

4. **Subscription Cancelled** (`subscription_cancelled.html`)
   - Enviado cuando se cancela una suscripción
   - Información sobre cuándo termina el acceso

5. **Payment Failed** (`payment_failed.html`)
   - Enviado cuando falla un pago
   - Instrucciones para actualizar método de pago

### **Uso del Servicio de Email**

```python
from app.services.email_service import email_service

# Enviar email de bienvenida
await email_service.send_welcome_email(user)

# Enviar confirmación de suscripción
await email_service.send_subscription_confirmation_email(user, "Pro Plan", 29.99)

# Enviar advertencia de uso
await email_service.send_usage_limit_warning_email(user, 85)
```

## 🎨 Componentes Frontend

### **PricingPlans Component**

Componente principal para mostrar planes de suscripción:

```tsx
import PricingPlans from './components/Subscription/PricingPlans';

<PricingPlans 
  currentPlan="basic"
  onPlanSelect={(plan) => console.log(plan)}
/>
```

### **Subscription Page**

Página completa de gestión de suscripciones con:
- Estado actual de suscripción
- Estadísticas de uso
- Acceso al portal de facturación
- Cancelación de suscripción

## 🔄 Flujo de Suscripción

### **1. Selección de Plan**
```mermaid
User selects plan → Frontend calls create-checkout → Redirect to Stripe
```

### **2. Procesamiento de Pago**
```mermaid
Stripe processes payment → Webhook to backend → Update user tier → Send confirmation email
```

### **3. Gestión de Suscripción**
```mermaid
User accesses billing portal → Stripe portal → Webhooks update backend → Email notifications
```

## 🔧 Configuración de Desarrollo

### **Variables de Entorno Requeridas**

```env
# Stripe
STRIPE_SECRET_KEY=sk_test_...
STRIPE_PUBLISHABLE_KEY=pk_test_...
STRIPE_WEBHOOK_SECRET=whsec_...
STRIPE_PRICE_BASIC=price_...
STRIPE_PRICE_PRO=price_...
STRIPE_PRICE_ENTERPRISE=price_...

# SendGrid
SENDGRID_API_KEY=SG...
FROM_EMAIL=test@example.com
FROM_NAME=PDF Extractor

# Base de datos
DATABASE_URL=sqlite:///./test.db  # Para desarrollo
```

### **Configuración de Webhooks en Stripe**

1. **URL del Webhook**: `http://localhost:9700/api/webhooks/stripe`
2. **Eventos a Escuchar**:
   - `customer.subscription.created`
   - `customer.subscription.updated`
   - `customer.subscription.deleted`
   - `invoice.payment_succeeded`
   - `invoice.payment_failed`
   - `checkout.session.completed`

### **Testing de Webhooks Localmente**

Usa Stripe CLI para testing local:

```bash
# Instalar Stripe CLI
# https://stripe.com/docs/stripe-cli

# Login
stripe login

# Forward webhooks
stripe listen --forward-to localhost:9700/api/webhooks/stripe

# Trigger test events
stripe trigger customer.subscription.created
```

## 🧪 Testing

### **Testing de Endpoints**

```python
import pytest
from fastapi.testclient import TestClient

def test_get_subscription_plans(client: TestClient):
    response = client.get("/api/subscription/plans")
    assert response.status_code == 200
    assert len(response.json()) == 4  # 4 planes
```

### **Testing de Emails**

```python
def test_send_welcome_email():
    # Mock SendGrid
    with patch('sendgrid.SendGridAPIClient.send') as mock_send:
        mock_send.return_value.status_code = 202
        
        result = await email_service.send_welcome_email(user)
        assert result == True
```

## 📊 Monitoreo

### **Métricas Importantes**

1. **Conversión de Planes**:
   - Free → Basic: X%
   - Basic → Pro: X%
   - Pro → Enterprise: X%

2. **Retención**:
   - Churn rate mensual
   - Lifetime Value (LTV)
   - Tiempo promedio en cada tier

3. **Uso del Sistema**:
   - Archivos procesados por tier
   - API calls por usuario
   - Tiempo de procesamiento promedio

### **Logs Importantes**

```python
import logging

logger = logging.getLogger(__name__)

# Eventos de suscripción
logger.info(f"User {user.id} upgraded to {new_tier}")

# Eventos de uso
logger.warning(f"User {user.id} reached 80% of usage limit")

# Eventos de pago
logger.error(f"Payment failed for user {user.id}: {error}")
```

## 🚀 Despliegue

### **Variables de Producción**

```env
ENVIRONMENT=production
DATABASE_URL=postgresql://user:pass@prod-db/database
STRIPE_SECRET_KEY=sk_live_...
SENDGRID_API_KEY=SG.production_key...
FRONTEND_URL=https://yourdomain.com
```

### **Consideraciones de Seguridad**

1. **Rate Limiting**: Implementar límites por IP y usuario
2. **Webhook Verification**: Verificar siempre las signatures de Stripe
3. **Input Validation**: Validar todos los inputs del usuario
4. **Environment Variables**: Nunca hardcodear secretos
5. **HTTPS**: Usar HTTPS en producción para webhooks

## 🔧 Mantenimiento

### **Tareas Periódicas**

1. **Limpiar archivos antiguos**: Ejecutar cleanup cada día
2. **Resetear contadores mensuales**: Al inicio de cada mes
3. **Verificar suscripciones**: Reconciliar con Stripe semanalmente
4. **Backup de base de datos**: Diario
5. **Monitorear logs de error**: Alertas automáticas

### **Actualizaciones de Precios**

Para cambiar precios:

1. Crear nuevos productos en Stripe
2. Actualizar variables de entorno con nuevos price_ids
3. Actualizar componente PricingPlans
4. Los usuarios existentes mantienen sus precios hasta renovación

---

## 📞 Contacto para Desarrolladores

- **Email técnico**: dev@pdfextractor.com
- **Documentación API**: http://localhost:9700/docs
- **Stripe Dashboard**: https://dashboard.stripe.com
- **SendGrid Dashboard**: https://app.sendgrid.com