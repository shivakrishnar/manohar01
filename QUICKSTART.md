# Quick Start - DEX Trigger Response Archive

## 🚀 Deploy in 5 Minutes

### Prerequisites
- AWS CLI installed and configured
- AWS SAM CLI installed
- Python 3.11+
- Valid AWS credentials with deployment permissions

### Step 1: Setup Secrets (2 minutes)

```bash
# Database credentials
aws secretsmanager create-secret \
    --name dex-archive/db-credentials \
    --secret-string '{
      "host": "your-db.rds.amazonaws.com",
      "username": "db_user",
      "password": "db_password",
      "database": "Mediant",
      "port": 1433
    }'

# API credentials
aws secretsmanager create-secret \
    --name dex-archive/api-credentials \
    --secret-string '{
      "token_url": "https://oauth.example.com/token",
      "client_id": "your_client_id",
      "client_secret": "your_client_secret"
    }'
```

### Step 2: Validate (30 seconds)

```bash
./validate.sh
```

### Step 3: Deploy (2-3 minutes)

```bash
./deploy.sh
```

Follow the prompts and provide:
- Stack name: `dex-trigger-archive-stack`
- Region: `us-east-1` (or your region)
- S3 bucket name: Choose unique name
- API base URL: Your DEX API endpoint

### Step 4: Test (30 seconds)

```bash
# Invoke Lambda
aws lambda invoke \
    --function-name dex-trigger-response-archive \
    --payload '{}' \
    response.json

# Check results
cat response.json

# Verify S3
aws s3 ls s3://YOUR-BUCKET-NAME/trigger/ --recursive
```

## ✅ You're Done!

The Lambda function is deployed and ready to:
- Query database for clients with dex/trigger:all scope
- Fetch trigger data from DEX API
- Archive responses to S3

## 🔄 Run on Schedule (Optional)

To run automatically M-F at 8:30 PM:

```bash
# Get function ARN
LAMBDA_ARN=$(aws lambda get-function \
    --function-name dex-trigger-response-archive \
    --query 'Configuration.FunctionArn' \
    --output text)

# Create schedule
aws events put-rule \
    --name dex-trigger-archive-schedule \
    --schedule-expression "cron(30 20 ? * MON-FRI *)" \
    --state ENABLED

# Link to Lambda
aws events put-targets \
    --rule dex-trigger-archive-schedule \
    --targets "Id"="1","Arn"="$LAMBDA_ARN"

# Grant permission
aws lambda add-permission \
    --function-name dex-trigger-response-archive \
    --statement-id EventBridgeInvoke \
    --action lambda:InvokeFunction \
    --principal events.amazonaws.com \
    --source-arn $(aws events describe-rule --name dex-trigger-archive-schedule --query Arn --output text)
```

## 📚 Documentation

- Full details: [README.md](README.md)
- Deployment guide: [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md)
- Secrets setup: [SECRETS_SETUP.md](SECRETS_SETUP.md)

## 🆘 Troubleshooting

**Can't connect to database?**
- Add VPC configuration with security groups and subnets
- Redeploy with VPC parameters

**Lambda timeout?**
- Increase timeout: `aws lambda update-function-configuration --function-name dex-trigger-response-archive --timeout 900`

**Need help?**
- Check logs: `aws logs tail /aws/lambda/dex-trigger-response-archive --follow`
