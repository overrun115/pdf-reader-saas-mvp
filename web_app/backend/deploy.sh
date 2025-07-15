#!/bin/bash

# 🚂 Railway Deployment Script for PDF Reader Backend
# ===================================================

echo "🚀 Starting Railway deployment preparation..."

# Check if we're in the right directory
if [ ! -f "app/main.py" ]; then
    echo "❌ Error: Run this script from the backend directory"
    exit 1
fi

# Create deployment directory
mkdir -p deployment

# Copy essential files for Railway
echo "📦 Preparing deployment files..."
cp Dockerfile.railway deployment/Dockerfile
cp railway.json deployment/
cp requirements.txt deployment/
cp -r app deployment/
cp .env.production deployment/.env

echo "✅ Files prepared for Railway deployment"
echo ""
echo "🎯 Next steps:"
echo "1. Push your code to GitHub"
echo "2. Connect Railway to your GitHub repo"
echo "3. Select the backend folder"
echo "4. Railway will auto-deploy using Dockerfile.railway"
echo ""
echo "🌍 Environment variables to set in Railway:"
echo "   - ENVIRONMENT=production"
echo "   - DEBUG=False"
echo "   - SECRET_KEY=O0syNHI3k-I0zcBafhmJaeNJ2KgkIWd2RaI_KiUXexk"
echo "   - Add PostgreSQL and Redis add-ons"
echo ""
echo "🔗 Railway URL: https://railway.app"