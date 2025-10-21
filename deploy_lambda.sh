#!/bin/bash

# AWS Lambda Deployment Script for Recipe Variety Fix
echo "🚀 Deploying Recipe Variety Fix to AWS Lambda..."

# Function name from your logs
FUNCTION_NAME="AyeAyeStack-CreateRecipeLambda2BD8AFF3-iuqdJg0lCo0I"

# Navigate to lambda directory
cd lambda/create-recipe

# Create deployment package
echo "📦 Creating deployment package..."
zip -r ../../create-recipe-deployment.zip . -x "*.pyc" "__pycache__/*" "test_*" "*.md"

# Go back to root
cd ../..

# Deploy to AWS Lambda
echo "🚀 Deploying to AWS Lambda..."
aws lambda update-function-code \
  --function-name $FUNCTION_NAME \
  --zip-file fileb://create-recipe-deployment.zip

if [ $? -eq 0 ]; then
    echo "✅ Deployment successful!"
    echo "🧪 Test your app now - you should see:"
    echo "  • Creamy Mango-Oat Breakfast Bowl Smoothie"
    echo "  • Green Mango-Spinach Power Smoothie"
    echo "  • Cocoa Mango 'Milkshake' (No-Peanut Base)"
    echo ""
    echo "❌ Instead of:"
    echo "  • Mango Smoothie Blend 1/2/3"
else
    echo "❌ Deployment failed. Check AWS CLI configuration."
fi

# Clean up
rm create-recipe-deployment.zip
echo "🧹 Cleaned up deployment package"