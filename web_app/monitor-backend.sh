#!/bin/bash

# Script para monitorear y reiniciar automáticamente el backend cuando se bloquea
# Uso: ./monitor-backend.sh

BACKEND_URL="http://localhost:8000/health"
MAX_RESPONSE_TIME=10  # segundos
CHECK_INTERVAL=30     # segundos entre checks
LOG_FILE="backend-monitor.log"

echo "$(date): Iniciando monitor del backend..." | tee -a $LOG_FILE

while true; do
    echo "$(date): Verificando backend..." >> $LOG_FILE
    
    # Hacer petición con timeout
    if timeout $MAX_RESPONSE_TIME curl -s $BACKEND_URL > /dev/null 2>&1; then
        echo "$(date): Backend responde correctamente" >> $LOG_FILE
    else
        echo "$(date): ⚠️ Backend no responde o timeout. Reiniciando..." | tee -a $LOG_FILE
        
        # Reiniciar backend
        docker-compose restart backend
        
        # Esperar a que inicie
        echo "$(date): Esperando a que el backend reinicie..." | tee -a $LOG_FILE
        sleep 20
        
        # Verificar si el reinicio fue exitoso
        if timeout $MAX_RESPONSE_TIME curl -s $BACKEND_URL > /dev/null 2>&1; then
            echo "$(date): ✅ Backend reiniciado exitosamente" | tee -a $LOG_FILE
        else
            echo "$(date): ❌ Fallo al reiniciar backend" | tee -a $LOG_FILE
        fi
    fi
    
    sleep $CHECK_INTERVAL
done