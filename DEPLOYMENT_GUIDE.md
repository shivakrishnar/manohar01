# Deployment Guide - DEX Trigger Response Archive

## Pre-Deployment Checklist

### ✅ Step 1: Install Required Tools

#### AWS CLI
```bash
# Linux/Mac
curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
unzip awscliv2.zip
sudo ./aws/install

# Verify
aws --version
```

#### AWS SAM CLI
```bash
# Linux (via Homebrew or pip)
pip install aws-sam-cli

# Or download from: https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/install-sam-cli.html

# Verify
sam --version
```

#### Python Dependencies (for local testing)
```bash
pip install boto3 pymssql requests pyyaml
```

### ✅ Step 2: Configure AWS Credentials

```bash
# Configure AWS CLI with your credentials
aws configure

# Provide:
# - AWS Access Key ID
# - AWS Secret Access Key
# - Default region (e.g., us-east-1)
# - Default output format (json)

# Verify
aws sts get-caller-identity
```

### ✅ Step 3: Create AWS Secrets

#### Database Credentials
```bash
aws secretsmanager create-secret \
    --name dex-archive/db-credentials \
    --description "Database credentials for DEX Trigger Archive" \
    --secret-string '{
      "host": "your-sqlserver.rds.amazonaws.com",
      "username": "your_db_user",
      "password": "your_db_password",
      "database": "Mediant",
      "port": 1433
    }'
```

#### API Credentials
```bash
aws secretsmanager create-secret \
    --name dex-archive/api-credentials \
    --description "API OAuth2 credentials for DEX API" \
    --secret-string '{
      "token_url": "https://your-oauth-server.com/oauth/token",
      "client_id": "your_client_id",
      "client_secret": "your_client_secret"
    }'
```

### ✅ Step 4: Prepare Configuration

```bash
# Copy environment template
cp .env.template .env

# Edit with your values
nano .env  # or use your preferred editor
```

Update these values in `.env`:
- `S3_BUCKET_NAME`: Choose a globally unique bucket name
- `DEX_API_BASE_URL`: Your DEX API endpoint
- `AWS_REGION`: Your AWS region
- `VPC_SECURITY_GROUP_IDS` and `VPC_SUBNET_IDS`: If using VPC

## Deployment Methods

### Method 1: Automated Deployment (Recommended)

```bash
# Run the deployment script
./deploy.sh
```

This will:
1. Validate prerequisites
2. Build the Lambda function
3. Deploy using SAM
4. Create all AWS resources

### Method 2: Manual SAM Deployment

```bash
# Build
sam build

# Deploy (first time - guided)
sam deploy --guided

# Follow prompts:
# - Stack name: dex-trigger-archive-stack
# - AWS Region: us-east-1 (or your region)
# - Parameter S3BucketName: your-unique-bucket-name
# - Parameter DBSecretName: dex-archive/db-credentials
# - Parameter APISecretName: dex-archive/api-credentials
# - Parameter DexApiBaseUrl: https://your-api.com
# - Confirm changes: Y
# - Allow SAM CLI IAM role creation: Y
# - Save arguments to samconfig.toml: Y

# Subsequent deployments
sam deploy
```

### Method 3: AWS CLI (CloudFormation)

```bash
# Package the application
sam package \
    --template-file template.yaml \
    --output-template-file packaged.yaml \
    --s3-bucket your-deployment-bucket

# Deploy
sam deploy \
    --template-file packaged.yaml \
    --stack-name dex-trigger-archive-stack \
    --capabilities CAPABILITY_NAMED_IAM \
    --parameter-overrides \
        S3BucketName=dex-trigger-archive \
        DBSecretName=dex-archive/db-credentials \
        APISecretName=dex-archive/api-credentials \
        DexApiBaseUrl=https://your-api.com
```

## Post-Deployment Verification

### 1. Verify Stack Creation

```bash
# Check stack status
aws cloudformation describe-stacks \
    --stack-name dex-trigger-archive-stack \
    --query 'Stacks[0].StackStatus'

# Should return: CREATE_COMPLETE or UPDATE_COMPLETE
```

### 2. Test Lambda Function

```bash
# Invoke function
aws lambda invoke \
    --function-name dex-trigger-response-archive \
    --payload '{}' \
    --cli-binary-format raw-in-base64-out \
    response.json

# Check response
cat response.json

# Expected output:
# {
#   "statusCode": 200,
#   "body": "{\"total_clients\": X, \"successful_archives\": Y, ...}"
# }
```

### 3. Check CloudWatch Logs

```bash
# View recent logs
aws logs tail /aws/lambda/dex-trigger-response-archive --follow

# Or view last 10 minutes
aws logs tail /aws/lambda/dex-trigger-response-archive --since 10m
```

### 4. Verify S3 Upload

```bash
# List archived files
aws s3 ls s3://dex-trigger-archive/trigger/ --recursive

# Example output:
# 2024-11-27 12:34:56    1024 trigger/12345/12345_trigger_20241127.json
# 2024-11-27 12:34:57    2048 trigger/67890/67890_trigger_20241127.json
```

### 5. Download and Inspect Archive

```bash
# Download a sample file
aws s3 cp s3://dex-trigger-archive/trigger/12345/12345_trigger_20241127.json .

# View contents
cat 12345_trigger_20241127.json | jq .
```

## Setting Up Scheduled Execution (Optional)

If you want the function to run on a schedule (e.g., M-F at 8:30 PM):

```bash
# Create EventBridge rule
aws events put-rule \
    --name dex-trigger-archive-schedule \
    --description "Triggers DEX archive at 8:30 PM M-F" \
    --schedule-expression "cron(30 20 ? * MON-FRI *)" \
    --state ENABLED

# Get Lambda function ARN
LAMBDA_ARN=$(aws lambda get-function \
    --function-name dex-trigger-response-archive \
    --query 'Configuration.FunctionArn' \
    --output text)

# Add Lambda as target
aws events put-targets \
    --rule dex-trigger-archive-schedule \
    --targets "Id"="1","Arn"="$LAMBDA_ARN"

# Grant EventBridge permission to invoke Lambda
aws lambda add-permission \
    --function-name dex-trigger-response-archive \
    --statement-id EventBridgeInvoke \
    --action lambda:InvokeFunction \
    --principal events.amazonaws.com \
    --source-arn arn:aws:events:$(aws configure get region):$(aws sts get-caller-identity --query Account --output text):rule/dex-trigger-archive-schedule

echo "✓ Scheduled execution configured!"
```

## Troubleshooting

### Issue: "Access Denied" when deploying

**Solution:**
```bash
# Verify AWS credentials
aws sts get-caller-identity

# Check IAM permissions - ensure you have:
# - CloudFormation full access
# - Lambda full access
# - S3 full access
# - IAM role creation
# - Secrets Manager read access
```

### Issue: Lambda timeout or out of memory

**Solution:**
```bash
# Increase timeout and memory
aws lambda update-function-configuration \
    --function-name dex-trigger-response-archive \
    --timeout 900 \
    --memory-size 1024
```

### Issue: Database connection fails

**Solution:**
1. Verify VPC configuration if database is in VPC
2. Check security group rules
3. Verify database credentials in Secrets Manager
4. Test connectivity from Lambda

```bash
# Update VPC configuration
sam deploy --parameter-overrides \
    VpcSecurityGroupIds="sg-xxxxx" \
    VpcSubnetIds="subnet-xxxxx,subnet-yyyyy"
```

### Issue: S3 bucket already exists

**Solution:**
```bash
# Choose a different bucket name
sam deploy --parameter-overrides S3BucketName=dex-trigger-archive-yourcompany-prod
```

## Updating the Deployment

### Update Lambda Code Only

```bash
# After modifying lambda_function.py
sam build
sam deploy

# Or quick update without SAM
zip function.zip lambda_function.py
aws lambda update-function-code \
    --function-name dex-trigger-response-archive \
    --zip-file fileb://function.zip
```

### Update Environment Variables

```bash
aws lambda update-function-configuration \
    --function-name dex-trigger-response-archive \
    --environment Variables="{
        S3_BUCKET_NAME=dex-trigger-archive,
        DB_SECRET_NAME=dex-archive/db-credentials,
        API_SECRET_NAME=dex-archive/api-credentials,
        DEX_API_BASE_URL=https://new-api.com,
        TRIGGER_DATE_OFFSET_DAYS=0
    }"
```

## Monitoring and Alerts

### View Lambda Metrics

```bash
# Get invocation count
aws cloudwatch get-metric-statistics \
    --namespace AWS/Lambda \
    --metric-name Invocations \
    --dimensions Name=FunctionName,Value=dex-trigger-response-archive \
    --start-time $(date -u -d '1 hour ago' +%Y-%m-%dT%H:%M:%S) \
    --end-time $(date -u +%Y-%m-%dT%H:%M:%S) \
    --period 3600 \
    --statistics Sum

# Get error count
aws cloudwatch get-metric-statistics \
    --namespace AWS/Lambda \
    --metric-name Errors \
    --dimensions Name=FunctionName,Value=dex-trigger-response-archive \
    --start-time $(date -u -d '1 hour ago' +%Y-%m-%dT%H:%M:%S) \
    --end-time $(date -u +%Y-%m-%dT%H:%M:%S) \
    --period 3600 \
    --statistics Sum
```

### Create SNS Alarm for Errors

```bash
# Create SNS topic
aws sns create-topic --name dex-archive-alerts

# Subscribe to topic (replace with your email)
aws sns subscribe \
    --topic-arn arn:aws:sns:REGION:ACCOUNT:dex-archive-alerts \
    --protocol email \
    --notification-endpoint your-email@example.com

# The alarm is already created by the template
# You can update the alarm to send to SNS:
aws cloudwatch put-metric-alarm \
    --alarm-name DexTriggerArchive-Lambda-Errors \
    --alarm-actions arn:aws:sns:REGION:ACCOUNT:dex-archive-alerts \
    --metric-name Errors \
    --namespace AWS/Lambda \
    --dimensions Name=FunctionName,Value=dex-trigger-response-archive \
    --period 300 \
    --evaluation-periods 1 \
    --threshold 1 \
    --comparison-operator GreaterThanOrEqualToThreshold \
    --statistic Sum
```

## Cleanup (Remove All Resources)

```bash
# Delete CloudFormation stack (removes most resources)
aws cloudformation delete-stack --stack-name dex-trigger-archive-stack

# Wait for deletion to complete
aws cloudformation wait stack-delete-complete --stack-name dex-trigger-archive-stack

# Empty and delete S3 bucket
aws s3 rm s3://dex-trigger-archive --recursive
aws s3 rb s3://dex-trigger-archive

# Delete secrets (optional)
aws secretsmanager delete-secret \
    --secret-id dex-archive/db-credentials \
    --force-delete-without-recovery

aws secretsmanager delete-secret \
    --secret-id dex-archive/api-credentials \
    --force-delete-without-recovery

# Delete EventBridge rule (if created)
aws events remove-targets --rule dex-trigger-archive-schedule --ids 1
aws events delete-rule --name dex-trigger-archive-schedule

echo "✓ All resources cleaned up!"
```

## Production Checklist

Before going to production:

- [ ] Database credentials configured in Secrets Manager
- [ ] API credentials configured in Secrets Manager
- [ ] VPC configuration set (if database in VPC)
- [ ] S3 bucket name is unique and appropriate
- [ ] CloudWatch alarms configured and tested
- [ ] Lambda timeout and memory adequate for client count
- [ ] Test execution completed successfully
- [ ] S3 lifecycle policies reviewed
- [ ] IAM roles follow least privilege
- [ ] Documentation updated with production values
- [ ] Monitoring dashboard created (optional)
- [ ] Schedule configured (if using EventBridge)

## Support

For issues during deployment:
1. Check CloudWatch Logs: `aws logs tail /aws/lambda/dex-trigger-response-archive`
2. Verify CloudFormation events: `aws cloudformation describe-stack-events --stack-name dex-trigger-archive-stack`
3. Review IAM permissions
4. Ensure all prerequisites are met
