# 🗄️ Migraciones de Base de Datos

## Campos Agregados para SaaS

### **Tabla: users**

Se agregaron los siguientes campos para soportar el sistema de suscripciones:

```sql
-- Campos agregados a la tabla users
ALTER TABLE users ADD COLUMN stripe_customer_id VARCHAR(255) NULL;
ALTER TABLE users ADD COLUMN subscription_end_date TIMESTAMP WITH TIME ZONE NULL;

-- Comentarios explicativos
COMMENT ON COLUMN users.stripe_customer_id IS 'ID del cliente en Stripe para gestión de pagos';
COMMENT ON COLUMN users.subscription_end_date IS 'Fecha de fin de la suscripción actual';
```

### **Campos Existentes Utilizados**

Los siguientes campos ya existían y se utilizan para el sistema SaaS:

- `tier` - Enum('free', 'basic', 'pro', 'enterprise')
- `subscription_id` - VARCHAR para ID de suscripción de Stripe
- `subscription_active` - BOOLEAN para estado de suscripción
- `files_processed_this_month` - INTEGER para conteo de uso
- `total_files_processed` - INTEGER para estadísticas

## Schema Completo de Usuario

```sql
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    full_name VARCHAR(255) NOT NULL,
    
    -- Subscription info
    tier user_tier_enum DEFAULT 'free',
    subscription_id VARCHAR(255) NULL,
    subscription_active BOOLEAN DEFAULT true,
    stripe_customer_id VARCHAR(255) NULL,
    subscription_end_date TIMESTAMP WITH TIME ZONE NULL,
    
    -- Usage tracking
    files_processed_this_month INTEGER DEFAULT 0,
    total_files_processed INTEGER DEFAULT 0,
    
    -- Account status
    is_active BOOLEAN DEFAULT true,
    is_verified BOOLEAN DEFAULT false,
    
    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    last_login TIMESTAMP WITH TIME ZONE NULL
);
```

## Script de Migración Manual

Si necesitas aplicar las migraciones manualmente:

```sql
-- 1. Verificar si las columnas ya existen
SELECT column_name 
FROM information_schema.columns 
WHERE table_name = 'users' 
AND column_name IN ('stripe_customer_id', 'subscription_end_date');

-- 2. Agregar columnas si no existen
DO $$ 
BEGIN
    -- Agregar stripe_customer_id si no existe
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'users' AND column_name = 'stripe_customer_id'
    ) THEN
        ALTER TABLE users ADD COLUMN stripe_customer_id VARCHAR(255) NULL;
    END IF;
    
    -- Agregar subscription_end_date si no existe
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'users' AND column_name = 'subscription_end_date'
    ) THEN
        ALTER TABLE users ADD COLUMN subscription_end_date TIMESTAMP WITH TIME ZONE NULL;
    END IF;
END $$;

-- 3. Crear índices para optimizar consultas
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_users_stripe_customer_id 
ON users(stripe_customer_id) WHERE stripe_customer_id IS NOT NULL;

CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_users_subscription_active 
ON users(subscription_active) WHERE subscription_active = true;

CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_users_tier 
ON users(tier);
```

## Verificación de Migración

Para verificar que las migraciones se aplicaron correctamente:

```sql
-- Verificar estructura de la tabla
\d users

-- Verificar que las columnas existen
SELECT 
    column_name, 
    data_type, 
    is_nullable, 
    column_default
FROM information_schema.columns 
WHERE table_name = 'users' 
AND column_name IN ('stripe_customer_id', 'subscription_end_date');

-- Verificar índices
SELECT indexname, indexdef 
FROM pg_indexes 
WHERE tablename = 'users' 
AND indexname LIKE '%stripe%' OR indexname LIKE '%subscription%' OR indexname LIKE '%tier%';
```

## Datos de Ejemplo

Para testing, puedes insertar datos de ejemplo:

```sql
-- Actualizar usuario existente con datos de Stripe
UPDATE users 
SET 
    stripe_customer_id = 'cus_test_customer_id',
    tier = 'pro',
    subscription_active = true,
    subscription_end_date = NOW() + INTERVAL '1 month'
WHERE email = 'admin@pdfextractor.com';

-- Verificar actualización
SELECT id, email, tier, subscription_active, stripe_customer_id, subscription_end_date
FROM users 
WHERE email = 'admin@pdfextractor.com';
```

## Rollback (Si es necesario)

Para revertir las migraciones:

```sql
-- CUIDADO: Esto eliminará los datos de las columnas
ALTER TABLE users DROP COLUMN IF EXISTS stripe_customer_id;
ALTER TABLE users DROP COLUMN IF EXISTS subscription_end_date;

-- Eliminar índices
DROP INDEX IF EXISTS idx_users_stripe_customer_id;
DROP INDEX IF EXISTS idx_users_subscription_active;
DROP INDEX IF EXISTS idx_users_tier;
```

## Usando Alembic (Recomendado)

Si usas Alembic para migraciones:

```bash
# Generar migración automática
cd web_app/backend
alembic revision --autogenerate -m "Add Stripe fields to users table"

# Aplicar migración
alembic upgrade head

# Ver historial de migraciones
alembic history

# Revertir migración (si es necesario)
alembic downgrade -1
```

## Notas Importantes

1. **Backup**: Siempre haz backup antes de ejecutar migraciones en producción
2. **Downtime**: Estas migraciones son no-destructivas y pueden ejecutarse en caliente
3. **Índices**: Los índices se crean con `CONCURRENTLY` para evitar locks
4. **Validación**: Siempre verifica que las migraciones se aplicaron correctamente

## Migraciones Futuras

Para futuras funcionalidades, considera agregar:

```sql
-- Para analytics más detallados
ALTER TABLE users ADD COLUMN last_subscription_change TIMESTAMP WITH TIME ZONE;
ALTER TABLE users ADD COLUMN previous_tier user_tier_enum;
ALTER TABLE users ADD COLUMN referral_code VARCHAR(50) UNIQUE;

-- Para tracking de uso más granular
CREATE TABLE usage_logs (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    action VARCHAR(100) NOT NULL,
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    metadata JSONB
);
```