# Contributing to Aye-Aye Chef

Thank you for your interest in contributing to Aye-Aye Chef! This document provides guidelines and instructions for contributing.

## 🚀 Quick Start

1. **Fork the repository**
2. **Clone your fork**
   ```bash
   git clone https://github.com/aditya2812/aye-aye-chef.git
   cd aye-aye-chef
   ```
3. **Install dependencies**
   ```bash
   cd mobile-app
   npm install
   ```
4. **Start development**
   ```bash
   npm run web
   ```

## 🏗️ Project Structure

```
aye-aye-chef/
├── mobile-app/          # React Native/Expo frontend
├── lambda/              # AWS Lambda functions
├── lib/                 # AWS CDK infrastructure
├── docs/                # Documentation
├── tests/               # Test files
└── scripts/             # Deployment scripts
```

## 🛠️ Development Setup

### Prerequisites
- Node.js 18+
- npm or yarn
- AWS CLI (for backend development)
- Expo CLI

### Frontend Development
```bash
cd mobile-app
npm install
npm run web          # Start web development server
npm run android      # Start Android development
npm run ios          # Start iOS development
```

### Backend Development
```bash
npm install
npm run deploy       # Deploy AWS infrastructure
```

## 📝 Making Changes

### 1. Create a Branch
```bash
git checkout -b feature/your-feature-name
```

### 2. Make Your Changes
- Follow existing code style
- Add tests for new features
- Update documentation as needed

### 3. Test Your Changes
```bash
# Frontend tests
cd mobile-app
npm test

# Backend tests
npm run test
```

### 4. Commit Your Changes
```bash
git add .
git commit -m "feat: add your feature description"
```

### 5. Push and Create PR
```bash
git push origin feature/your-feature-name
```

## 🎯 Areas for Contribution

### Frontend (React Native/Expo)
- UI/UX improvements
- New features for ingredient detection
- Recipe display enhancements
- Mobile responsiveness
- Accessibility improvements

### Backend (AWS Lambda)
- Recipe generation algorithms
- Ingredient detection accuracy
- API performance optimization
- New cuisine support
- Nutrition data integration

### AI/ML
- Improve ingredient recognition
- Recipe variety and creativity
- Cuisine-specific recipe logic
- Dietary restriction handling

### Documentation
- API documentation
- User guides
- Developer tutorials
- Architecture documentation

## 🧪 Testing

### Frontend Testing
```bash
cd mobile-app
npm test                    # Run unit tests
npm run test:e2e           # Run end-to-end tests
```

### Backend Testing
```bash
npm run test:lambda        # Test Lambda functions
npm run test:integration   # Integration tests
```

## 📋 Code Style

### JavaScript/React Native
- Use ES6+ features
- Follow React hooks patterns
- Use meaningful variable names
- Add JSDoc comments for functions

### Python (Lambda functions)
- Follow PEP 8 style guide
- Use type hints
- Add docstrings for functions
- Handle errors gracefully

## 🐛 Bug Reports

When reporting bugs, please include:
- Steps to reproduce
- Expected behavior
- Actual behavior
- Screenshots (if applicable)
- Device/browser information
- Console errors

## 💡 Feature Requests

For feature requests, please provide:
- Clear description of the feature
- Use case and benefits
- Mockups or examples (if applicable)
- Implementation suggestions

## 🔒 Security

If you discover security vulnerabilities, please:
- **DO NOT** open a public issue
- Email security concerns to: security@ayeayechef.com
- Include detailed steps to reproduce

## 📄 License

By contributing, you agree that your contributions will be licensed under the MIT License.

## 🤝 Code of Conduct

### Our Pledge
We pledge to make participation in our project a harassment-free experience for everyone.

### Our Standards
- Use welcoming and inclusive language
- Be respectful of differing viewpoints
- Accept constructive criticism gracefully
- Focus on what is best for the community

## 🆘 Getting Help

- 📧 Email: support@ayeayechef.com
- 🐛 Issues: [GitHub Issues](https://github.com/aditya2812/aye-aye-chef/issues)
- 💬 Discussions: [GitHub Discussions](https://github.com/aditya2812/aye-aye-chef/discussions)

## 🎉 Recognition

Contributors will be recognized in:
- README.md contributors section
- Release notes
- Project documentation

Thank you for contributing to Aye-Aye Chef! 🍳✨