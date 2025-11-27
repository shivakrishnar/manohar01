# DEX-API Trigger Response Archive

AWS Lambda function to archive DEX-API trigger file responses to S3 for client investigation and audit purposes.

## Overview

This serverless application automates the archiving of DEX-API trigger responses. When invoked, it:

1. Query the Mediant database for clients with `dex/trigger:all` scope
2. Fetch trigger data from the `/data-exchange/trigger` endpoint for each client
3. Save responses as JSON files to S3 with organized folder structure

## Architecture

- **AWS Lambda**: Serverless compute for running the archive process
- **Amazon S3**: Storage for archived trigger responses
- **AWS Secrets Manager**: Secure storage for database and API credentials
- **Amazon RDS (SQL Server)**: Mediant database for client queries
- **CloudWatch Logs**: Application logging and monitoring

## Prerequisites

### Required Tools

1. **AWS CLI** - [Installation Guide](https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html)
2. **AWS SAM CLI** - [Installation Guide](https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/install-sam-cli.html)
3. **Python 3.11** or later
4. **Docker** (for SAM build)

### AWS Permissions

Your AWS user/role needs permissions for:
- CloudFormation (create/update stacks)
- Lambda (create/update functions)
- S3 (create buckets, put objects)
- IAM (create roles and policies)
- Secrets Manager (get secret values)
- CloudWatch Logs (create log groups)

## Setup Instructions

### 1. Clone or Download the Project

```bash
cd dex-trigger-response-archive
```

### 2. Configure AWS Secrets Manager

Create two secrets in AWS Secrets Manager with your credentials:

**Database Credentials Secret:**
```bash
aws secretsmanager create-secret \
    --name dex-archive/db-credentials \
    --description "Database credentials for DEX Trigger Archive" \
    --secret-string '{
      "host": "your-rds-endpoint.rds.amazonaws.com",
      "username": "your_db_user",
      "password": "your_db_password",
      "database": "Mediant",
      "port": 1433
    }'
```

**API Credentials Secret:**
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

See [SECRETS_SETUP.md](SECRETS_SETUP.md) for detailed instructions.

### 3. Update Configuration

Copy the environment template and update with your values:

```bash
cp .env.template .env
# Edit .env with your specific values
```

Key configurations to update:
- `S3_BUCKET_NAME`: Unique S3 bucket name for your account
- `DEX_API_BASE_URL`: Your DEX API endpoint
- `AWS_REGION`: Your AWS region

### 4. Build the Lambda Function

```bash
sam build
```

This will:
- Install Python dependencies from `requirements.txt`
- Package the Lambda function code
- Prepare for deployment

### 5. Deploy to AWS

**First-time deployment:**
```bash
sam deploy --guided
```

Follow the prompts:
- Stack name: `dex-trigger-archive-stack`
- AWS Region: (your region)
- Parameter S3BucketName: (your unique bucket name)
- Parameter DBSecretName: `dex-archive/db-credentials`
- Parameter APISecretName: `dex-archive/api-credentials`
- Parameter DexApiBaseUrl: (your DEX API URL)
- Confirm changes before deploy: Y
- Allow SAM CLI IAM role creation: Y
- Save arguments to configuration file: Y

**Subsequent deployments:**
```bash
sam deploy
```

### 6. Verify Deployment

Check that resources were created:

```bash
# List CloudFormation stacks
aws cloudformation describe-stacks --stack-name dex-trigger-archive-stack

# Check Lambda function
aws lambda get-function --function-name dex-trigger-response-archive

# Check S3 bucket
aws s3 ls | grep dex-trigger-archive

# Check EventBridge rule
aws events list-rules --name-prefix dex-trigger-archive
```

## File Structure

```
dex-trigger-response-archive/
├── lambda_function.py          # Main Lambda handler
├── requirements.txt            # Python dependencies
├── template.yaml              # SAM/CloudFormation template
├── .env.template              # Environment configuration template
├── SECRETS_SETUP.md           # Secrets Manager setup guide
├── README.md                  # This file
└── .gitignore                 # Git ignore file
```

## S3 Folder Structure

Archived files are stored in S3 with the following structure:

```
s3://dex-trigger-archive/
└── trigger/
    ├── [clientid1]/
    │   ├── [clientid1]_trigger_20241127.json
    │   └── [clientid1]_trigger_20241128.json
    ├── [clientid2]/
    │   ├── [clientid2]_trigger_20241127.json
    │   └── [clientid2]_trigger_20241128.json
    └── ...
```

**File naming convention:** `[clientid]_trigger_[yyyymmdd].json`

## Triggering the Function

The Lambda function can be triggered in multiple ways:

### 1. Manual Invocation via AWS Console
- Navigate to Lambda → Functions → dex-trigger-response-archive
- Click "Test" and create a test event with empty JSON `{}`
- Click "Test" to execute

### 2. AWS CLI
```bash
aws lambda invoke \
    --function-name dex-trigger-response-archive \
    --payload '{}' \
    response.json
```

### 3. EventBridge Schedule (Optional)
To add scheduled execution, create an EventBridge rule:
```bash
# Create rule for M-F at 8:30 PM UTC
aws events put-rule \
    --name dex-trigger-archive-schedule \
    --schedule-expression "cron(30 20 ? * MON-FRI *)" \
    --state ENABLED

# Add Lambda as target
aws events put-targets \
    --rule dex-trigger-archive-schedule \
    --targets "Id"="1","Arn"="arn:aws:lambda:REGION:ACCOUNT:function:dex-trigger-response-archive"

# Grant EventBridge permission to invoke Lambda
aws lambda add-permission \
    --function-name dex-trigger-response-archive \
    --statement-id EventBridgeInvoke \
    --action lambda:InvokeFunction \
    --principal events.amazonaws.com \
    --source-arn arn:aws:events:REGION:ACCOUNT:rule/dex-trigger-archive-schedule
```

### 4. Other AWS Services
- **Step Functions**: Orchestrate as part of larger workflow
- **API Gateway**: Expose as HTTP endpoint
- **S3 Events**: Trigger on file upload
- **SNS/SQS**: Event-driven invocation

## Testing

### Invoke and Verify

```bash
# Invoke Lambda function
aws lambda invoke \
    --function-name dex-trigger-response-archive \
    --payload '{}' \
    response.json

# View response
cat response.json

# Check S3 for archived files
aws s3 ls s3://dex-trigger-archive/trigger/ --recursive
```

### Check Logs

```bash
# View recent logs
sam logs --stack-name dex-trigger-archive-stack --tail

# Or use AWS CLI
aws logs tail /aws/lambda/dex-trigger-response-archive --follow
```

## Monitoring

### CloudWatch Alarms

Two alarms are automatically created:

1. **Lambda Errors Alarm**: Triggers when function has errors
2. **Lambda Duration Alarm**: Triggers when execution time approaches timeout

### View Metrics

```bash
# Get Lambda metrics
aws cloudwatch get-metric-statistics \
    --namespace AWS/Lambda \
    --metric-name Invocations \
    --dimensions Name=FunctionName,Value=dex-trigger-response-archive \
    --start-time 2024-11-27T00:00:00Z \
    --end-time 2024-11-27T23:59:59Z \
    --period 3600 \
    --statistics Sum
```

## Troubleshooting

### Common Issues

**1. Lambda timeout errors**
- Increase timeout in `template.yaml` (current: 900 seconds)
- Check database connection performance
- Verify network connectivity (VPC configuration if used)

**2. Permission denied errors**
- Verify IAM role has correct permissions
- Check Secrets Manager access
- Ensure S3 bucket permissions are correct

**3. Database connection failures**
- Verify database credentials in Secrets Manager
- Check security group rules (allow Lambda IP/SG)
- Ensure RDS instance is accessible from Lambda (VPC config)

**4. API authentication failures**
- Verify API credentials in Secrets Manager
- Check OAuth2 token endpoint URL
- Ensure client has correct scopes

### View Detailed Logs

```bash
# Stream live logs
aws logs tail /aws/lambda/dex-trigger-response-archive --follow

# Search for errors
aws logs filter-log-events \
    --log-group-name /aws/lambda/dex-trigger-response-archive \
    --filter-pattern "ERROR"
```

## Updating the Function

After making code changes:

```bash
# Rebuild and redeploy
sam build
sam deploy
```

For quick testing without full deployment:
```bash
# Deploy just the Lambda code
sam build
aws lambda update-function-code \
    --function-name dex-trigger-response-archive \
    --zip-file fileb://.aws-sam/build/DexTriggerArchiveFunction/lambda_function.zip
```

## Database Query Reference

The Lambda function executes this SQL query to identify clients:

```sql
SELECT DISTINCT c.ClientID, c.name 
FROM Client c
INNER JOIN ClientServiceExt cs ON c.ClientID = cs.ClientID 
WHERE c.OAuth2ClientCredentialsID IS NOT NULL
AND cs.ServiceID IN (2,8,3,4,5)
```

**ServiceID Mapping:**
- 2, 8, 3, 4, 5: Services that support `dex/trigger:all` scope

## API Endpoint Details

**Endpoint:** `/data-exchange/trigger`  
**Method:** GET  
**Authentication:** OAuth2 Bearer Token  
**Required Scope:** `dex/trigger:all`

**Query Parameters:**
- `clientId`: Client ID (integer)
- `triggerDate`: Date in YYYY-MM-DD format

## Cost Estimation

Estimated monthly costs (assuming 22 business days):

- **Lambda**: ~$0.20-$2.00 (depending on execution time and client count)
- **S3**: ~$0.02-$0.10 per GB stored (plus transfer costs)
- **Secrets Manager**: $0.80 per secret ($1.60 total for 2 secrets)
- **CloudWatch Logs**: ~$0.50 (first 5GB free)

**Total: ~$2-$4 per month** (based on 22 executions)

## Security Considerations

1. **Secrets Management**: All credentials stored in AWS Secrets Manager
2. **Encryption**: S3 bucket uses AES-256 encryption at rest
3. **Access Control**: IAM roles follow principle of least privilege
4. **Network**: VPC support for database connectivity (optional)
5. **Logging**: CloudWatch logs for audit trail
6. **S3 Security**: Public access blocked on bucket

## Cleanup

To remove all resources:

```bash
# Delete CloudFormation stack
aws cloudformation delete-stack --stack-name dex-trigger-archive-stack

# Delete secrets (optional)
aws secretsmanager delete-secret --secret-id dex-archive/db-credentials --force-delete-without-recovery
aws secretsmanager delete-secret --secret-id dex-archive/api-credentials --force-delete-without-recovery

# Empty and delete S3 bucket (if needed)
aws s3 rm s3://dex-trigger-archive --recursive
aws s3 rb s3://dex-trigger-archive
```

## Support

For issues or questions:
1. Check CloudWatch Logs for error details
2. Verify Secrets Manager configuration
3. Test database and API connectivity
4. Review IAM permissions

## Related Documentation

- [AWS Lambda Developer Guide](https://docs.aws.amazon.com/lambda/)
- [AWS SAM Documentation](https://docs.aws.amazon.com/serverless-application-model/)
- [AWS Secrets Manager](https://docs.aws.amazon.com/secretsmanager/)
- [EventBridge Schedule Expressions](https://docs.aws.amazon.com/eventbridge/latest/userguide/eb-create-rule-schedule.html)

## License

Internal use only - DEX-API Archive Project
