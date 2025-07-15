# 🌍 **VARIABLES DE ENTORNO PARA DEPLOYMENT**

## 🚂 **RAILWAY (Backend)**

### **Variables Requeridas:**
```bash
# Application
ENVIRONMENT=production
DEBUG=False
SECRET_KEY=O0syNHI3k-I0zcBafhmJaeNJ2KgkIWd2RaI_KiUXexk

# Database - Railway PostgreSQL (automático)
DATABASE_URL=${DATABASE_URL}

# Redis - Railway Redis (automático)
REDIS_URL=${REDIS_URL}

# CORS - Actualizar cuando tengas dominio
ALLOWED_ORIGINS=https://your-frontend-domain.vercel.app,https://your-custom-domain.com
```

### **Variables Opcionales (para cuando tengas claves):**
```bash
# Stripe
STRIPE_SECRET_KEY=sk_live_your_stripe_secret_key
STRIPE_PUBLISHABLE_KEY=pk_live_your_stripe_publishable_key
STRIPE_WEBHOOK_SECRET=whsec_your_webhook_secret
STRIPE_PRICE_BASIC=price_your_basic_price_id
STRIPE_PRICE_PRO=price_your_pro_price_id

# Email
SENDGRID_API_KEY=SG.your_sendgrid_api_key
FROM_EMAIL=noreply@yourdomain.com
FROM_NAME=PDF Reader
FRONTEND_URL=https://your-frontend-domain.vercel.app
```

## ⚡ **VERCEL (Frontend)**

### **Variables Requeridas:**
```bash
# API Configuration
REACT_APP_API_URL=https://your-backend-railway-url.railway.app

# Environment
REACT_APP_ENVIRONMENT=production

# Build optimization
GENERATE_SOURCEMAP=false
INLINE_RUNTIME_CHUNK=false
```

### **Variables Opcionales:**
```bash
# Stripe (cuando tengas claves)
REACT_APP_STRIPE_PUBLISHABLE_KEY=pk_live_your_stripe_publishable_key

# Analytics
REACT_APP_ENABLE_ANALYTICS=true
```

## 🔧 **CÓMO CONFIGURAR**

### **Railway:**
1. Ve a tu proyecto en railway.app
2. Selecciona tu servicio backend
3. Ve a "Variables" 
4. Añade las variables una por una
5. Redeploy automático

### **Vercel:**
1. Ve a tu proyecto en vercel.com
2. Settings → Environment Variables
3. Añade las variables
4. Redeploy

## 🎯 **ORDEN DE CONFIGURACIÓN**

1. **Backend primero** (Railway)
2. **Obtener URL del backend** 
3. **Configurar frontend** (Vercel) con URL del backend
4. **Conectar dominio** (opcional)
5. **Configurar Stripe** (cuando tengas claves)

## 🔒 **SECRETOS IMPORTANTES**

- **SECRET_KEY**: YA GENERADA - usar la de .env.production
- **DATABASE_URL**: Railway la genera automáticamente
- **STRIPE_KEYS**: Obtener de Stripe dashboard
- **SENDGRID_API_KEY**: Obtener de SendGrid (opcional para MVP)

## 📝 **NOTAS**

- Railway PostgreSQL y Redis son **GRATUITOS** hasta cierto límite
- Vercel deployment es **GRATUITO** para proyectos personales
- Stripe funciona sin configuración inicial (solo para pagos)
- SendGrid es opcional para MVP (los emails fallarán pero no rompe la app)