# 🚀 Deployment Guide

## Quick Deployment

### Prerequisites
- AWS Account with appropriate permissions
- Node.js 18+
- AWS CLI configured
- Expo CLI installed

### 1. Deploy Backend Infrastructure
```bash
# Install dependencies
npm install

# Deploy AWS resources
npm run deploy
```

### 2. Configure Frontend
```bash
# Copy environment template
cp mobile-app/.env.example mobile-app/.env

# Update with your AWS configuration
# (Use outputs from CDK deployment)
```

### 3. Deploy Frontend
```bash
cd mobile-app
npm run deploy:netlify
```

## Detailed Setup

See [SETUP.md](../SETUP.md) for complete setup instructions.

## Environment Configuration

### Required AWS Services
- Lambda Functions
- API Gateway
- S3 Bucket
- RDS PostgreSQL
- Cognito User Pool
- Bedrock Agent

### Environment Variables
```bash
EXPO_PUBLIC_USER_POOL_ID=your-cognito-user-pool-id
EXPO_PUBLIC_USER_POOL_CLIENT_ID=your-cognito-client-id
EXPO_PUBLIC_API_URL=your-api-gateway-url
EXPO_PUBLIC_IMAGES_BUCKET=your-s3-bucket-name
EXPO_PUBLIC_AWS_REGION=your-aws-region
```

## Deployment Options

### Option 1: Netlify (Recommended)
- Free tier with 100GB bandwidth
- Automatic HTTPS and CDN
- Easy custom domain setup

### Option 2: Vercel
- Similar to Netlify
- Excellent performance
- GitHub integration

### Option 3: AWS S3 + CloudFront
- Full AWS integration
- Custom configuration options
- Professional deployment

## Monitoring

- CloudWatch logs for Lambda functions
- API Gateway metrics
- RDS performance insights
- Custom application metrics

## Security Considerations

- Enable AWS CloudTrail
- Configure VPC security groups
- Use least privilege IAM roles
- Enable encryption at rest and in transit