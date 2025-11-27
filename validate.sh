#!/bin/bash

# Quick validation script to check all files are ready for deployment

set -e

echo "=========================================="
echo "DEX Trigger Archive - Validation Check"
echo "=========================================="
echo ""

ERRORS=0

# Check file existence
echo "Checking required files..."
FILES=("lambda_function.py" "requirements.txt" "template.yaml" "README.md" ".env.template")

for file in "${FILES[@]}"; do
    if [ -f "$file" ]; then
        echo "✓ $file exists"
    else
        echo "✗ $file missing"
        ((ERRORS++))
    fi
done

echo ""

# Validate Python syntax
echo "Validating Python syntax..."
if python3 -m py_compile lambda_function.py 2>/dev/null; then
    echo "✓ lambda_function.py syntax valid"
else
    echo "✗ lambda_function.py has syntax errors"
    ((ERRORS++))
fi

echo ""

# Check for AWS CLI
echo "Checking AWS CLI..."
if command -v aws &> /dev/null; then
    echo "✓ AWS CLI installed"
    AWS_VERSION=$(aws --version 2>&1)
    echo "  Version: $AWS_VERSION"
else
    echo "⚠ AWS CLI not installed (required for deployment)"
fi

echo ""

# Check for SAM CLI
echo "Checking SAM CLI..."
if command -v sam &> /dev/null; then
    echo "✓ SAM CLI installed"
    SAM_VERSION=$(sam --version 2>&1)
    echo "  Version: $SAM_VERSION"
else
    echo "⚠ SAM CLI not installed (required for deployment)"
fi

echo ""

# Check for Python
echo "Checking Python..."
if command -v python3 &> /dev/null; then
    echo "✓ Python 3 installed"
    PYTHON_VERSION=$(python3 --version 2>&1)
    echo "  Version: $PYTHON_VERSION"
else
    echo "✗ Python 3 not installed"
    ((ERRORS++))
fi

echo ""

# Validate YAML syntax
echo "Validating template.yaml..."
if python3 -c "import yaml; yaml.safe_load(open('template.yaml'))" 2>/dev/null; then
    echo "✓ template.yaml is valid YAML"
else
    echo "⚠ template.yaml may have YAML syntax issues (install PyYAML: pip install pyyaml)"
fi

echo ""

# Check environment template
echo "Checking environment configuration..."
if [ -f .env.template ]; then
    echo "✓ .env.template found"
    if [ -f .env ]; then
        echo "✓ .env exists (configured)"
    else
        echo "⚠ .env not found (copy from .env.template)"
    fi
fi

echo ""
echo "=========================================="

if [ $ERRORS -eq 0 ]; then
    echo "✓ All validation checks passed!"
    echo "=========================================="
    echo ""
    echo "Ready to deploy! Run: ./deploy.sh"
    exit 0
else
    echo "✗ Found $ERRORS error(s)"
    echo "=========================================="
    echo ""
    echo "Please fix errors before deployment"
    exit 1
fi
