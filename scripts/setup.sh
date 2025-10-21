#!/bin/bash

# Aye Aye Setup Script - Handle environment setup

set -e

echo "🔧 Setting up Aye Aye development environment..."

# Set environment variable to silence Node.js version warning
export JSII_SILENCE_WARNING_UNTESTED_NODE_VERSION=1

# Check Node.js version
NODE_VERSION=$(node --version)
echo "📋 Node.js version: $NODE_VERSION"

# Check if we have the required tools
echo "🔍 Checking prerequisites..."

# Check AWS CLI
if ! command -v aws &> /dev/null; then
    echo "❌ AWS CLI not found. Please install it first:"
    echo "   https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html"
    exit 1
fi

# Check if AWS is configured
if ! aws sts get-caller-identity > /dev/null 2>&1; then
    echo "❌ AWS CLI not configured. Please run 'aws configure' first."
    exit 1
fi

# Check jq
if ! command -v jq &> /dev/null; then
    echo "❌ jq not found. Installing via package manager..."
    if command -v brew &> /dev/null; then
        brew install jq
    elif command -v apt-get &> /dev/null; then
        sudo apt-get update && sudo apt-get install -y jq
    else
        echo "Please install jq manually: https://stedolan.github.io/jq/download/"
        exit 1
    fi
fi

echo "✅ Prerequisites check complete!"

# Install global dependencies
echo "📦 Installing global dependencies..."
npm install -g aws-cdk@2.160.0 @expo/cli

echo "✅ Setup complete! You can now run:"
echo "   ./scripts/deploy.sh"