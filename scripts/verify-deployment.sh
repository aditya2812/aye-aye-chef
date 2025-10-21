#!/bin/bash

# Aye Aye Deployment Verification Script

set -e

echo "🔍 Verifying Aye Aye deployment..."

# Check if stack exists
if ! aws cloudformation describe-stacks --stack-name AyeAyeStack > /dev/null 2>&1; then
    echo "❌ AyeAyeStack not found. Please run deployment first."
    exit 1
fi

echo "✅ CloudFormation stack found"

# Get stack outputs
STACK_OUTPUTS=$(aws cloudformation describe-stacks --stack-name AyeAyeStack --query 'Stacks[0].Outputs' --output json)

USER_POOL_ID=$(echo $STACK_OUTPUTS | jq -r '.[] | select(.OutputKey=="UserPoolId") | .OutputValue')
API_URL=$(echo $STACK_OUTPUTS | jq -r '.[] | select(.OutputKey=="ApiUrl") | .OutputValue')
IMAGES_BUCKET=$(echo $STACK_OUTPUTS | jq -r '.[] | select(.OutputKey=="ImagesBucketName") | .OutputValue')
DB_CLUSTER_ARN=$(echo $STACK_OUTPUTS | jq -r '.[] | select(.OutputKey=="DatabaseClusterArn") | .OutputValue')

echo "✅ Stack outputs retrieved"

# Check Cognito User Pool
if aws cognito-idp describe-user-pool --user-pool-id $USER_POOL_ID > /dev/null 2>&1; then
    echo "✅ Cognito User Pool is accessible"
else
    echo "❌ Cognito User Pool check failed"
fi

# Check S3 bucket
if aws s3 ls s3://$IMAGES_BUCKET > /dev/null 2>&1; then
    echo "✅ S3 bucket is accessible"
else
    echo "❌ S3 bucket check failed"
fi

# Check API Gateway
if curl -s -o /dev/null -w "%{http_code}" $API_URL | grep -q "403\|401"; then
    echo "✅ API Gateway is responding (auth required as expected)"
else
    echo "⚠️  API Gateway response unexpected (might be OK)"
fi

# Check DynamoDB tables
if aws dynamodb describe-table --table-name usda_cache > /dev/null 2>&1; then
    echo "✅ DynamoDB usda_cache table exists"
else
    echo "❌ DynamoDB usda_cache table check failed"
fi

if aws dynamodb describe-table --table-name fdc_label_cache > /dev/null 2>&1; then
    echo "✅ DynamoDB fdc_label_cache table exists"
else
    echo "❌ DynamoDB fdc_label_cache table check failed"
fi

# Check Aurora cluster
if aws rds describe-db-clusters --db-cluster-identifier $(echo $DB_CLUSTER_ARN | cut -d':' -f6) > /dev/null 2>&1; then
    echo "✅ Aurora cluster is accessible"
else
    echo "❌ Aurora cluster check failed"
fi

# Check mobile app environment
if [ -f "mobile-app/.env" ]; then
    echo "✅ Mobile app environment file exists"
    echo "📱 Mobile app configuration:"
    cat mobile-app/.env
else
    echo "❌ Mobile app environment file missing"
fi

echo ""
echo "🎉 Deployment verification complete!"
echo ""
echo "📋 Next Steps:"
echo "1. Set up database schema (see README.md)"
echo "2. Add USDA API key to Secrets Manager"
echo "3. Test mobile app: cd mobile-app && npx expo start"