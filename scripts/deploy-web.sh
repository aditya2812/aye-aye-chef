#!/bin/bash

# Aye-Aye Chef Web Deployment Script
# This script builds and deploys the mobile app as a web application

set -e  # Exit on any error

echo "🚀 Starting Aye-Aye Chef Web Deployment..."

# Navigate to mobile app directory
cd mobile-app

echo "📦 Installing dependencies..."
npm install

echo "🔧 Building web application..."
npx expo export:web

echo "✅ Build completed! Files are in web-build/ directory"

# Check if Netlify CLI is installed
if command -v netlify &> /dev/null; then
    echo "🌐 Deploying to Netlify..."
    cd web-build
    netlify deploy --prod --dir .
    echo "✅ Deployed to Netlify!"
elif command -v vercel &> /dev/null; then
    echo "🌐 Deploying to Vercel..."
    cd web-build
    vercel --prod
    echo "✅ Deployed to Vercel!"
else
    echo "📁 Build complete! To deploy:"
    echo "   1. Install Netlify CLI: npm install -g netlify-cli"
    echo "   2. Run: netlify deploy --prod --dir web-build"
    echo "   OR"
    echo "   1. Go to netlify.com"
    echo "   2. Drag and drop the web-build folder"
fi

echo "🎉 Deployment process complete!"