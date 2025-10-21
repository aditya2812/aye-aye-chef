#!/bin/bash

# Aye Aye Infrastructure Deployment Script

set -e

# Silence Node.js version warnings
export JSII_SILENCE_WARNING_UNTESTED_NODE_VERSION=1

echo "🚀 Starting Aye Aye infrastructure deployment..."

# Check if AWS CLI is configured
if ! aws sts get-caller-identity > /dev/null 2>&1; then
    echo "❌ AWS CLI not configured. Please run 'aws configure' first."
    exit 1
fi

# Install dependencies
echo "📦 Installing dependencies..."
npm install

# Build Lambda layer
echo "🔧 Building Lambda layer..."
mkdir -p lambda-layers/common/python
cd lambda-layers/common/python

# Use a virtual environment to avoid conflicts
python3 -m venv temp_venv
source temp_venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt -t .
deactivate
rm -rf temp_venv

cd ../../../

# Bootstrap CDK (if not already done)
echo "🏗️  Bootstrapping CDK..."
npx cdk bootstrap

# Deploy infrastructure
echo "🚀 Deploying infrastructure..."
npx cdk deploy --require-approval never

# Get outputs
echo "📋 Getting deployment outputs..."
STACK_OUTPUTS=$(aws cloudformation describe-stacks --stack-name AyeAyeStack --query 'Stacks[0].Outputs' --output json)

USER_POOL_ID=$(echo $STACK_OUTPUTS | jq -r '.[] | select(.OutputKey=="UserPoolId") | .OutputValue')
USER_POOL_CLIENT_ID=$(echo $STACK_OUTPUTS | jq -r '.[] | select(.OutputKey=="UserPoolClientId") | .OutputValue')
API_URL=$(echo $STACK_OUTPUTS | jq -r '.[] | select(.OutputKey=="ApiUrl") | .OutputValue')
IMAGES_BUCKET=$(echo $STACK_OUTPUTS | jq -r '.[] | select(.OutputKey=="ImagesBucketName") | .OutputValue')
DB_CLUSTER_ARN=$(echo $STACK_OUTPUTS | jq -r '.[] | select(.OutputKey=="DatabaseClusterArn") | .OutputValue')
DB_SECRET_ARN=$(echo $STACK_OUTPUTS | jq -r '.[] | select(.OutputKey=="DatabaseSecretArn") | .OutputValue')

# Create environment file for mobile app
echo "📱 Creating mobile app environment file..."
cat > mobile-app/.env << EOF
EXPO_PUBLIC_USER_POOL_ID=$USER_POOL_ID
EXPO_PUBLIC_USER_POOL_CLIENT_ID=$USER_POOL_CLIENT_ID
EXPO_PUBLIC_API_URL=$API_URL
EXPO_PUBLIC_IMAGES_BUCKET=$IMAGES_BUCKET
EXPO_PUBLIC_AWS_REGION=$(aws configure get region)
EOF

echo "✅ Infrastructure deployed successfully!"
echo ""
echo "📋 Deployment Summary:"
echo "   User Pool ID: $USER_POOL_ID"
echo "   User Pool Client ID: $USER_POOL_CLIENT_ID"
echo "   API URL: $API_URL"
echo "   Images Bucket: $IMAGES_BUCKET"
echo ""
echo "🔧 Next Steps:"
echo "1. Set up the database schema:"
echo "   aws rds-data execute-statement --resource-arn $DB_CLUSTER_ARN --secret-arn $DB_SECRET_ARN --database ayeaye --sql \"\$(cat scripts/setup-database.sql)\""
echo ""
echo "2. Add your USDA API key to Secrets Manager:"
echo "   aws secretsmanager update-secret --secret-id aye-aye/usda-api-key --secret-string '{\"api_key\":\"YOUR_USDA_API_KEY\"}'"
echo ""
echo "3. Build and run the mobile app:"
echo "   cd mobile-app && npm install && npx expo start"