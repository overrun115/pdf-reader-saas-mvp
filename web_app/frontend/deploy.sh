#!/bin/bash

# ⚡ Vercel Deployment Script for PDF Reader Frontend
# ==================================================

echo "🚀 Starting Vercel deployment preparation..."

# Check if we're in the right directory
if [ ! -f "package.json" ]; then
    echo "❌ Error: Run this script from the frontend directory"
    exit 1
fi

# Install dependencies if needed
if [ ! -d "node_modules" ]; then
    echo "📦 Installing dependencies..."
    npm install
fi

# Build the project
echo "🔨 Building production version..."
npm run build

# Check if build was successful
if [ ! -d "build" ]; then
    echo "❌ Build failed!"
    exit 1
fi

echo "✅ Build successful!"
echo ""
echo "🎯 Next steps:"
echo "1. Install Vercel CLI: npm i -g vercel"
echo "2. Run: vercel --prod"
echo "3. Follow the prompts"
echo ""
echo "🌍 Environment variables to set in Vercel:"
echo "   - REACT_APP_API_URL=https://your-railway-backend-url.railway.app"
echo "   - REACT_APP_ENVIRONMENT=production"
echo "   - GENERATE_SOURCEMAP=false"
echo ""
echo "🔗 Vercel Dashboard: https://vercel.com/dashboard"