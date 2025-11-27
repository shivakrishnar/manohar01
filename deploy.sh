#!/bin/bash

# Deployment script for DEX Trigger Response Archive Lambda Function
# This script automates the build and deployment process

set -e

echo "=========================================="
echo "DEX Trigger Archive - Deployment Script"
echo "=========================================="
echo ""

# Check required tools
echo "Checking prerequisites..."

if ! command -v aws &> /dev/null; then
    echo "ERROR: AWS CLI is not installed. Please install it first."
    exit 1
fi

if ! command -v sam &> /dev/null; then
    echo "ERROR: AWS SAM CLI is not installed. Please install it first."
    exit 1
fi

if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python 3 is not installed. Please install it first."
    exit 1
fi

echo "✓ All prerequisites met"
echo ""

# Load environment variables if .env exists
if [ -f .env ]; then
    echo "Loading environment variables from .env..."
    export $(cat .env | grep -v '^#' | xargs)
    echo "✓ Environment variables loaded"
else
    echo "WARNING: .env file not found. Using default values."
fi

echo ""

# Validate AWS credentials
echo "Validating AWS credentials..."
if aws sts get-caller-identity &> /dev/null; then
    ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
    echo "✓ AWS credentials valid (Account: $ACCOUNT_ID)"
else
    echo "ERROR: AWS credentials are not configured or invalid."
    exit 1
fi

echo ""

# Build Lambda function
echo "Building Lambda function..."
sam build
echo "✓ Build completed"
echo ""

# Deploy
echo "Deploying to AWS..."
if [ -f samconfig.toml ]; then
    echo "Using existing samconfig.toml configuration"
    sam deploy
else
    echo "Running guided deployment (first time)"
    sam deploy --guided
fi

echo ""
echo "=========================================="
echo "Deployment completed successfully!"
echo "=========================================="
echo ""
echo "Next steps:"
echo "1. Verify the Lambda function in AWS Console"
echo "2. Check CloudWatch Logs for any issues"
echo "3. Test the function manually if needed:"
echo "   aws lambda invoke --function-name dex-trigger-response-archive --payload '{}' response.json"
echo ""
