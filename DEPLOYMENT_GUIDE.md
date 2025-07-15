# 🚀 **GUÍA COMPLETA DE DEPLOYMENT GRATUITO**

## 🎯 **OBJETIVO**
Deployar tu PDF Reader SaaS **100% GRATIS** usando Railway (backend) + Vercel (frontend) + PostgreSQL/Redis gratuitos.

---

## 📋 **PREREQUISITOS**

- [ ] Cuenta GitHub (gratis)
- [ ] Cuenta Railway (gratis) - railway.app
- [ ] Cuenta Vercel (gratis) - vercel.com
- [ ] Git instalado localmente

---

## 🚂 **PASO 1: DEPLOY BACKEND EN RAILWAY**

### **1.1 Crear cuenta y proyecto**
1. Ve a [railway.app](https://railway.app)
2. Regístrate con GitHub
3. Crear nuevo proyecto → "Deploy from GitHub repo"
4. Selecciona tu repositorio PDF Reader

### **1.2 Configurar servicios**
1. **Añadir PostgreSQL**: 
   - New Service → Database → PostgreSQL
   - Railway genera `DATABASE_URL` automáticamente

2. **Añadir Redis**:
   - New Service → Database → Redis  
   - Railway genera `REDIS_URL` automáticamente

3. **Configurar Backend**:
   - New Service → GitHub Repo → web_app/backend
   - Railway detecta `Dockerfile.railway` automáticamente

### **1.3 Variables de entorno**
En Railway backend service → Settings → Environment:

```bash
# CRÍTICAS - Configurar AHORA
ENVIRONMENT=production
DEBUG=False
SECRET_KEY=O0syNHI3k-I0zcBafhmJaeNJ2KgkIWd2RaI_KiUXexk

# AUTOMÁTICAS - Railway las genera
DATABASE_URL=${{Postgres.DATABASE_URL}}
REDIS_URL=${{Redis.REDIS_URL}}

# ACTUALIZARÁS DESPUÉS - cuando tengas frontend URL
ALLOWED_ORIGINS=https://your-frontend.vercel.app
FRONTEND_URL=https://your-frontend.vercel.app

# OPCIONALES - para cuando tengas claves
STRIPE_SECRET_KEY=sk_live_xxx
SENDGRID_API_KEY=SG.xxx
```

### **1.4 Deploy y obtener URL**
1. Railway hace deploy automático
2. Ve a Settings → Networking → Generate Domain
3. Copia la URL: `https://your-app-production.railway.app`
4. **GUARDA ESTA URL** - la necesitas para el frontend

---

## ⚡ **PASO 2: DEPLOY FRONTEND EN VERCEL**

### **2.1 Preparar repositorio**
1. Asegúrate que el código esté en GitHub
2. Frontend debe estar en `web_app/frontend/`

### **2.2 Crear proyecto Vercel**
1. Ve a [vercel.com](https://vercel.com)
2. Regístrate con GitHub
3. Import Git Repository → Selecciona tu repo
4. Root Directory: `web_app/frontend`
5. Framework Preset: Create React App
6. Click "Deploy"

### **2.3 Variables de entorno**
En Vercel project → Settings → Environment Variables:

```bash
# CRÍTICA - URL de tu backend Railway
REACT_APP_API_URL=https://your-app-production.railway.app

# CONFIGURACIÓN
REACT_APP_ENVIRONMENT=production
GENERATE_SOURCEMAP=false
INLINE_RUNTIME_CHUNK=false

# OPCIONAL - cuando tengas Stripe
REACT_APP_STRIPE_PUBLISHABLE_KEY=pk_live_xxx
```

### **2.4 Actualizar CORS en backend**
1. Ve a Railway backend → Environment Variables
2. Actualiza `ALLOWED_ORIGINS` con tu URL de Vercel:
   ```bash
   ALLOWED_ORIGINS=https://your-frontend.vercel.app,https://your-custom-domain.com
   ```

---

## 🔧 **PASO 3: CONFIGURACIÓN POST-DEPLOYMENT**

### **3.1 Test de conectividad**
1. Abre tu frontend URL
2. Intenta registro de usuario
3. Verifica que backend responde

### **3.2 Configurar Stripe (cuando tengas claves)**
1. Crea cuenta Stripe
2. Obtén claves de API
3. Actualiza variables en Railway y Vercel
4. Configura webhooks: `https://your-backend.railway.app/api/webhooks/stripe`

### **3.3 Dominio personalizado (opcional)**
1. **Vercel**: Settings → Domains → Add custom domain
2. **Railway**: Settings → Networking → Custom domain

---

## 🚨 **TROUBLESHOOTING**

### **Backend no responde**
```bash
# Ver logs en Railway
railway logs

# Check health
curl https://your-backend.railway.app/api/health
```

### **Frontend no conecta**
1. Verificar `REACT_APP_API_URL` en Vercel
2. Verificar CORS en Railway backend
3. Check browser console for errors

### **Base de datos no conecta**
1. Verificar `DATABASE_URL` en Railway
2. Check PostgreSQL service status
3. Ver logs de backend

### **Errores comunes**
- **CORS Error**: Actualizar `ALLOWED_ORIGINS` 
- **500 Error**: Check backend logs en Railway
- **Build Error**: Verificar dependencies en `package.json`

---

## 💰 **COSTOS Y LÍMITES GRATUITOS**

### **Railway (Gratis):**
- $5 crédito mensual
- PostgreSQL: 1GB storage
- Redis: 100MB
- 500 horas ejecución/mes

### **Vercel (Gratis):**
- 100GB bandwidth/mes
- Deploys ilimitados
- Custom domains: 1 por proyecto

### **Cuándo necesitarás pagar:**
- Railway: >500 horas/mes ($5-20/mes)
- Vercel: >100GB bandwidth ($20/mes)
- **Para MVP**: 6-12 meses gratis fácilmente

---

## ✅ **CHECKLIST DE DEPLOYMENT**

### **Pre-deployment:**
- [ ] Código en GitHub
- [ ] Secrets configurados
- [ ] CORS configurado
- [ ] Health checks funcionando

### **Backend (Railway):**
- [ ] PostgreSQL service running
- [ ] Redis service running  
- [ ] Backend deployed y healthy
- [ ] Environment variables configuradas
- [ ] Domain generado

### **Frontend (Vercel):**
- [ ] Build exitoso
- [ ] Environment variables configuradas
- [ ] CORS actualizado en backend
- [ ] Frontend carga correctamente

### **Testing:**
- [ ] Health check responde
- [ ] Registro de usuario funciona
- [ ] Upload de PDF funciona
- [ ] No hay errores CORS
- [ ] Logs limpios

---

## 🎯 **PRÓXIMOS PASOS DESPUÉS DE DEPLOYMENT**

1. **Testing exhaustivo**
2. **Configurar Stripe** para pagos
3. **Añadir dominio personalizado**
4. **Configurar SendGrid** para emails
5. **Monitoreo básico**
6. **Documentos legales** (Privacy Policy, Terms)

---

## 📞 **SOPORTE**

Si tienes problemas:
1. Check logs en Railway/Vercel dashboards
2. Verificar variables de entorno
3. Test endpoints individualmente
4. Browser developer tools para frontend

**¡Tu SaaS estará online en 30-60 minutos!** 🎉