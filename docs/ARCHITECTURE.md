# 🏗️ Aye-Aye Chef Architecture

## System Overview

Aye-Aye Chef is built on a modern, serverless architecture using AWS services for scalability and reliability.

## Architecture Diagram

![Architecture Diagram](aye-aye-chef-architecture-clean.drawio)

## Components

### Frontend (React Native/Expo)
- **Mobile App**: Cross-platform React Native application
- **Web App**: Expo web build for browser access
- **Authentication**: AWS Cognito integration
- **Camera Integration**: Image capture and upload

### API Layer
- **API Gateway**: REST API endpoints with CORS
- **Authentication**: JWT token validation
- **Rate Limiting**: Request throttling and protection

### Backend Services (AWS Lambda)
- **Image Processing**: S3 presigned URLs and upload handling
- **Ingredient Detection**: Computer vision with AWS Bedrock
- **Recipe Generation**: AI-powered recipe creation
- **Data Management**: Database operations and user preferences

### AI Services
- **Amazon Bedrock Agent**: AI orchestration and decision making
- **Claude LLM**: Natural language recipe generation
- **Bedrock Vision**: Image recognition and ingredient detection
- **USDA API**: Nutrition data integration

### Data Storage
- **Amazon S3**: Image and asset storage
- **Amazon RDS**: PostgreSQL database for structured data
- **AWS Secrets Manager**: Secure credential storage
- **CloudWatch**: Monitoring and logging

## Data Flow

1. **Image Capture**: User takes/selects ingredient photo
2. **Upload**: Image uploaded to S3 via presigned URL
3. **Detection**: Bedrock Vision analyzes image for ingredients
4. **Confirmation**: User confirms/modifies detected ingredients
5. **Generation**: Bedrock Agent creates personalized recipes
6. **Display**: Formatted recipes shown to user

## Security

- **Authentication**: AWS Cognito with JWT tokens
- **Authorization**: Role-based access control
- **Encryption**: HTTPS/TLS for all communications
- **Data Protection**: Encrypted storage and secure APIs

## Scalability

- **Serverless**: Auto-scaling Lambda functions
- **CDN**: CloudFront for global content delivery
- **Database**: RDS with read replicas for high availability
- **Monitoring**: CloudWatch for performance tracking

## Technology Stack

### Frontend
- React Native 0.75+
- Expo SDK 54+
- React Navigation 6+
- AWS Amplify

### Backend
- AWS Lambda (Python 3.11)
- AWS API Gateway
- AWS Bedrock
- PostgreSQL 15+

### Infrastructure
- AWS CDK (TypeScript)
- CloudFormation
- GitHub Actions (CI/CD)