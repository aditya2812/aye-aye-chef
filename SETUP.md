# 🛠️ Aye-Aye Chef Setup Guide

Complete setup instructions for developers and contributors.

> **Development Note**: This project was developed using [Kiro IDE](https://kiro.ai), an AI-powered development environment that significantly accelerated development through intelligent code generation, automated testing, and seamless AWS integration.

## 📋 Prerequisites

### Required Software
- **Node.js** 18+ ([Download](https://nodejs.org/))
- **npm** or **yarn** (comes with Node.js)
- **Git** ([Download](https://git-scm.com/))
- **AWS CLI** ([Install Guide](https://aws.amazon.com/cli/))
- **Expo CLI** (installed via npm)

### AWS Account Setup
1. Create an [AWS Account](https://aws.amazon.com/)
2. Configure AWS CLI with your credentials
3. Ensure you have permissions for:
   - Lambda, API Gateway, S3, RDS, Cognito, Bedrock

## 🚀 Quick Start

### 1. Clone Repository
```bash
git clone https://github.com/aditya2812/aye-aye-chef.git
cd aye-aye-chef
```

### 2. Install Dependencies
```bash
# Root dependencies (AWS CDK)
npm install

# Mobile app dependencies
cd mobile-app
npm install
cd ..
```

### 3. Environment Setup
```bash
# Copy environment template
cp mobile-app/.env.example mobile-app/.env

# Edit with your AWS configuration
nano mobile-app/.env
```

### 4. Deploy Backend Infrastructure
```bash
# Deploy AWS resources
npm run deploy

# Note the API Gateway URL from output
```

### 5. Update Frontend Configuration
```bash
# Update mobile-app/.env with your API Gateway URL
EXPO_PUBLIC_API_URL=https://your-api-gateway-url.amazonaws.com/prod/
```

### 6. Start Development
```bash
cd mobile-app
npm run web
```

## 🏗️ Detailed Setup

### Backend Infrastructure (AWS CDK)

#### 1. Install AWS CDK
```bash
npm install -g aws-cdk
```

#### 2. Bootstrap CDK (first time only)
```bash
cdk bootstrap
```

#### 3. Deploy Infrastructure
```bash
npm run deploy
```

This creates:
- **Lambda Functions** for recipe generation
- **API Gateway** for REST endpoints
- **S3 Bucket** for image storage
- **RDS Database** for data persistence
- **Cognito User Pool** for authentication
- **Bedrock Agent** for AI recipe generation

#### 4. Configure Environment Variables
After deployment, update `mobile-app/.env` with the output values:
```bash
EXPO_PUBLIC_USER_POOL_ID=us-west-2_xxxxxxxxx
EXPO_PUBLIC_USER_POOL_CLIENT_ID=xxxxxxxxxxxxxxxxxx
EXPO_PUBLIC_API_URL=https://xxxxxxxxxx.execute-api.us-west-2.amazonaws.com/prod/
EXPO_PUBLIC_IMAGES_BUCKET=aye-aye-images-xxxxxxxxxx
EXPO_PUBLIC_AWS_REGION=us-west-2
```

### Frontend Development (React Native/Expo)

#### 1. Install Expo CLI
```bash
npm install -g @expo/cli
```

#### 2. Start Development Server
```bash
cd mobile-app
npm run web          # Web development
npm run android      # Android (requires Android Studio)
npm run ios          # iOS (requires Xcode on macOS)
```

#### 3. Build for Production
```bash
npm run build:web    # Build web version
```

## 🌐 Deployment Options

### Option 1: Netlify (Recommended)
```bash
cd mobile-app
npm run deploy:netlify
```

### Option 2: Vercel
```bash
cd mobile-app
npm run deploy:vercel
```

### Option 3: Manual Deployment
```bash
cd mobile-app
npm run build:web
# Upload dist/ folder to your hosting provider
```

## 🧪 Testing

### Run All Tests
```bash
npm test
```

### Frontend Tests
```bash
cd mobile-app
npm test
```

### Backend Tests
```bash
npm run test:lambda
```

### Integration Tests
```bash
npm run test:integration
```

## 🔧 Configuration

### Environment Variables

#### Mobile App (.env)
```bash
# AWS Configuration
EXPO_PUBLIC_USER_POOL_ID=your-cognito-user-pool-id
EXPO_PUBLIC_USER_POOL_CLIENT_ID=your-cognito-client-id
EXPO_PUBLIC_API_URL=your-api-gateway-url
EXPO_PUBLIC_IMAGES_BUCKET=your-s3-bucket-name
EXPO_PUBLIC_AWS_REGION=your-aws-region

# Optional: Development settings
EXPO_PUBLIC_DEBUG_MODE=true
```

#### AWS CDK (cdk.json)
```json
{
  "app": "npx ts-node --prefer-ts-exts bin/aye-aye-chef.ts",
  "context": {
    "environment": "development",
    "region": "us-west-2"
  }
}
```

## 🐛 Troubleshooting

### Common Issues

#### 1. AWS Permissions Error
```bash
# Ensure AWS CLI is configured
aws configure list

# Check permissions
aws sts get-caller-identity
```

#### 2. Expo Build Fails
```bash
# Clear cache
cd mobile-app
rm -rf node_modules dist .expo
npm install
```

#### 3. Lambda Deployment Fails
```bash
# Check AWS region and permissions
# Ensure CDK is bootstrapped
cdk bootstrap
```

#### 4. CORS Issues
- Check API Gateway CORS configuration
- Ensure proper headers in Lambda responses

### Getting Help
- 📧 Email: support@ayeayechef.com
- 🐛 Issues: [GitHub Issues](https://github.com/aditya2812/aye-aye-chef/issues)
- 📖 Documentation: [docs/](docs/)

## 📁 Project Structure

```
aye-aye-chef/
├── README.md                    # Main documentation
├── SETUP.md                     # This file
├── CONTRIBUTING.md              # Contribution guidelines
├── LICENSE                      # MIT License
├── package.json                 # Root dependencies
├── cdk.json                     # CDK configuration
├── mobile-app/                  # Frontend application
│   ├── src/                     # Source code
│   ├── assets/                  # Images, icons
│   ├── package.json             # Frontend dependencies
│   └── .env                     # Environment variables
├── lambda/                      # Backend functions
│   ├── create-recipe/           # Recipe generation
│   ├── detect-ingredients/      # Image processing
│   └── ...                      # Other functions
├── lib/                         # AWS CDK infrastructure
├── docs/                        # Documentation
├── tests/                       # Test files
└── scripts/                     # Deployment scripts
```

## 🎯 Next Steps

1. **Explore the code** - Start with `mobile-app/src/`
2. **Run tests** - Ensure everything works
3. **Make changes** - Follow the contributing guide
4. **Deploy** - Test your changes live
5. **Contribute** - Submit pull requests

Happy coding! 🚀