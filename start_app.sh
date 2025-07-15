#!/bin/bash
# Script para levantar toda la app PDF Table Extractor de forma sencilla

set -e

cd "$(dirname "$0")/web_app"
echo "Construyendo y levantando todos los servicios..."
docker-compose up --build
