# Monitor Automático del Backend

## Problema
El backend ocasionalmente se bloquea por consultas SQL lentas o problemas de memoria, causando timeouts en el frontend.

## Solución Automática

### 1. Monitor en Background
Ejecuta este comando en una terminal separada para monitoreo automático:

```bash
cd /Users/leandrodebagge/code/pdf_reader/web_app
./monitor-backend.sh
```

### 2. ¿Qué hace el monitor?
- ✅ Verifica el backend cada 30 segundos
- ⚠️ Detecta timeouts o no respuesta
- 🔄 Reinicia automáticamente el backend si hay problemas  
- ✅ Confirma que el reinicio fue exitoso
- 📝 Guarda logs en `backend-monitor.log`

### 3. Logs del Monitor
```bash
# Ver logs en tiempo real
tail -f backend-monitor.log

# Ver logs completos
cat backend-monitor.log
```

## Mejoras del Frontend

### 1. React Query Optimizado
- **Cache inteligente**: 30s stale time, 5min cache time
- **Retry logic**: Máximo 2 reintentos con backoff exponencial
- **No refetch**: En window focus para reducir consultas

### 2. Timeouts Optimizados
- **API normal**: 15 segundos (era 30s)
- **File API**: 2 minutos para uploads
- **Status polling**: 8 segundos con fetch + AbortController

### 3. Estados Visuales
- **Loading**: Indicador cuando cargan archivos
- **Error**: Alerta con botón retry cuando hay problemas
- **Timeout detection**: Mensaje específico para timeouts

## Uso Manual

### Reiniciar Backend Manualmente
```bash
cd /Users/leandrodebagge/code/pdf_reader/web_app
docker-compose restart backend
```

### Verificar Estado
```bash
# Check health
curl http://localhost:8000/health

# Check containers
docker ps
```

### Ver Logs del Backend
```bash
docker logs web_app-backend-1 --tail 50
```

## Comandos Útiles

### Iniciar Todo el Sistema
```bash
cd /Users/leandrodebagge/code/pdf_reader/web_app

# Iniciar servicios
docker-compose up -d

# Iniciar monitor (terminal separada)
./monitor-backend.sh

# Iniciar frontend (terminal separada)
cd frontend && npm start
```

### Parar Monitor
- Presiona `Ctrl+C` en la terminal del monitor

### Optimización de Base de Datos
Si los problemas persisten, considerar:
```bash
# Reiniciar PostgreSQL para limpiar conexiones
docker-compose restart postgres

# Ver estadísticas de consultas
docker exec -it web_app-postgres-1 psql -U pdf_user -d pdf_extractor -c "SELECT * FROM pg_stat_activity;"
```

## Notas
- El monitor funciona solo en macOS/Linux
- Requiere `curl` y `timeout` commands
- Los logs se acumulan - limpia `backend-monitor.log` periódicamente
- El frontend es resiliente a fallos temporales del backend