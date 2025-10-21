#!/bin/bash

# Quick deployment script for Aye-Aye Chef
echo "🚀 Building and deploying Aye-Aye Chef web app..."

cd mobile-app

echo "📦 Building web app..."
npm run build:web

echo "✅ Build complete! Your app is ready to deploy."
echo ""
echo "🌐 To deploy to Netlify:"
echo "   1. Go to https://app.netlify.com/drop"
echo "   2. Drag the 'mobile-app/dist' folder to the page"
echo "   3. Get your public URL!"
echo ""
echo "📁 Build files are in: mobile-app/dist/"

# Open the dist folder in finder (macOS)
if [[ "$OSTYPE" == "darwin"* ]]; then
    open dist/
fi