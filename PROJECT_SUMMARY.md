# DEX Trigger Response Archive - Project Summary

## 📋 Project Overview

**Purpose:** Archive DEX-API trigger file responses to S3 for client investigation and audit purposes

**Ticket:** DEX-API-Archive Trigger File Response (from Median) and archive load Segment Position data

**Epic:** ProdSupport/Client Implementation Optimization

## 🏗️ Architecture

```
┌─────────────────┐
│  EventBridge    │ (Optional - Schedule trigger)
│  or Manual      │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Lambda         │ ◄─── Secrets Manager (DB & API credentials)
│  Python 3.11    │
└────────┬────────┘
         │
         ├─────► RDS SQL Server (Query clients)
         │
         ├─────► DEX API (Fetch trigger data)
         │
         └─────► S3 Bucket (Archive JSON files)
```

## 📁 File Structure

```
dex-trigger-response-archive/
├── lambda_function.py          # Main Lambda handler (11KB)
├── requirements.txt            # Python dependencies
├── template.yaml              # AWS SAM/CloudFormation template
├── .env.template              # Environment configuration template
├── .gitignore                 # Git ignore rules
│
├── deploy.sh                  # Automated deployment script
├── validate.sh                # Pre-deployment validation
├── test_lambda.py             # Local testing script
│
├── QUICKSTART.md              # 5-minute deployment guide
├── DEPLOYMENT_GUIDE.md        # Comprehensive deployment instructions
├── SECRETS_SETUP.md           # AWS Secrets Manager setup
└── README.md                  # Full documentation
```

## 🎯 Key Features

✅ **Database Integration:** Queries SQL Server for clients with dex/trigger:all scope
✅ **OAuth2 Authentication:** Secure API access with token management
✅ **S3 Archival:** Organized folder structure `trigger/[clientid]/[clientid]_trigger_[yyyymmdd].json`
✅ **Error Handling:** Comprehensive logging and error recovery
✅ **Secrets Management:** Credentials in AWS Secrets Manager
✅ **Monitoring:** CloudWatch Logs and alarms
✅ **Flexible Triggering:** Manual, scheduled, or event-driven
✅ **Production Ready:** VPC support, encryption, IAM least privilege

## 🗄️ Database Query

```sql
SELECT DISTINCT c.ClientID, c.name 
FROM Client c
INNER JOIN ClientServiceExt cs ON c.ClientID = cs.ClientID 
WHERE c.OAuth2ClientCredentialsID IS NOT NULL
AND cs.ServiceID IN (2,8,3,4,5)
```

## 🌐 API Integration

**Endpoint:** `/data-exchange/trigger`
**Method:** GET
**Authentication:** OAuth2 Bearer Token
**Scope:** `dex/trigger:all`

**Parameters:**
- `clientId`: Client ID (integer)
- `triggerDate`: Date in YYYY-MM-DD format

## 📦 S3 Archive Structure

```
s3://dex-trigger-archive/
└── trigger/
    ├── 12345/
    │   ├── 12345_trigger_20241127.json
    │   ├── 12345_trigger_20241128.json
    │   └── ...
    ├── 67890/
    │   ├── 67890_trigger_20241127.json
    │   └── ...
    └── ...
```

**File naming:** `[clientid]_trigger_[yyyymmdd].json`

## 🔧 AWS Resources Created

| Resource | Name/ID | Purpose |
|----------|---------|---------|
| Lambda Function | `dex-trigger-response-archive` | Main processing logic |
| S3 Bucket | `dex-trigger-archive` (configurable) | Archive storage |
| IAM Role | `DexTriggerArchiveLambdaRole` | Lambda execution permissions |
| Log Group | `/aws/lambda/dex-trigger-response-archive` | CloudWatch Logs |
| CloudWatch Alarm | `DexTriggerArchive-Lambda-Errors` | Error monitoring |
| CloudWatch Alarm | `DexTriggerArchive-Lambda-Duration` | Duration monitoring |
| Secret | `dex-archive/db-credentials` | Database credentials |
| Secret | `dex-archive/api-credentials` | API OAuth2 credentials |

## 🚀 Deployment Options

### Option 1: Automated (Recommended)
```bash
./deploy.sh
```

### Option 2: AWS SAM
```bash
sam build
sam deploy --guided
```

### Option 3: AWS CLI
```bash
sam package --s3-bucket deployment-bucket
sam deploy --template-file packaged.yaml --stack-name dex-trigger-archive-stack
```

## 📊 Cost Estimate

| Service | Monthly Cost |
|---------|-------------|
| Lambda (22 executions) | ~$0.20 - $2.00 |
| S3 Storage | ~$0.02 - $0.10 per GB |
| Secrets Manager (2 secrets) | $1.60 |
| CloudWatch Logs | ~$0.50 (first 5GB free) |
| **Total** | **~$2 - $4/month** |

## 🔒 Security Features

- ✅ Secrets stored in AWS Secrets Manager (encrypted)
- ✅ S3 bucket encryption at rest (AES-256)
- ✅ S3 versioning enabled
- ✅ Public access blocked on S3
- ✅ IAM least privilege roles
- ✅ VPC support for database connectivity
- ✅ CloudWatch audit logs

## 📈 Monitoring & Alerts

**CloudWatch Metrics:**
- Invocations
- Errors
- Duration
- Throttles

**Alarms:**
1. Lambda Errors (>= 1 error in 5 minutes)
2. Lambda Duration (> 14 minutes warning)

**Logs:**
```bash
aws logs tail /aws/lambda/dex-trigger-response-archive --follow
```

## 🔄 Execution Flow

1. **Trigger:** Function invoked (manual, scheduled, or event-driven)
2. **Authentication:** Retrieve OAuth2 access token
3. **Database Query:** Get clients with dex/trigger:all scope
4. **API Calls:** Fetch trigger data for each client
5. **Archive:** Save JSON responses to S3
6. **Response:** Return summary of successes/failures

## 🧪 Testing

```bash
# Validate code
./validate.sh

# Test locally (requires AWS credentials)
python3 test_lambda.py

# Invoke in AWS
aws lambda invoke \
    --function-name dex-trigger-response-archive \
    --payload '{}' \
    response.json
```

## 📝 Environment Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `S3_BUCKET_NAME` | S3 bucket for archives | `dex-trigger-archive` |
| `DB_SECRET_NAME` | Database credentials secret | `dex-archive/db-credentials` |
| `API_SECRET_NAME` | API credentials secret | `dex-archive/api-credentials` |
| `DEX_API_BASE_URL` | DEX API endpoint | `https://api.example.com` |
| `TRIGGER_DATE_OFFSET_DAYS` | Date offset (0 = today) | `0` |

## 🛠️ Maintenance

### Update Code
```bash
sam build
sam deploy
```

### Update Environment Variables
```bash
aws lambda update-function-configuration \
    --function-name dex-trigger-response-archive \
    --environment Variables="{...}"
```

### View Logs
```bash
aws logs tail /aws/lambda/dex-trigger-response-archive --follow
```

### Delete Stack
```bash
aws cloudformation delete-stack --stack-name dex-trigger-archive-stack
```

## 📚 Documentation

| Document | Purpose |
|----------|---------|
| [QUICKSTART.md](QUICKSTART.md) | 5-minute deployment guide |
| [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md) | Comprehensive deployment steps |
| [SECRETS_SETUP.md](SECRETS_SETUP.md) | Secrets Manager configuration |
| [README.md](README.md) | Full project documentation |

## ✅ Production Readiness Checklist

- [x] Python code validated (no syntax errors)
- [x] AWS SAM template validated
- [x] Security best practices implemented
- [x] Error handling and logging
- [x] CloudWatch monitoring and alarms
- [x] Documentation complete
- [x] Deployment scripts provided
- [x] Validation script included
- [x] Testing guide provided
- [x] Cost estimation documented

## 🎯 Next Steps

1. **Deploy:** Run `./deploy.sh`
2. **Configure Secrets:** Set up database and API credentials
3. **Test:** Invoke Lambda function manually
4. **Schedule (Optional):** Set up EventBridge rule
5. **Monitor:** Check CloudWatch Logs and metrics

## 📞 Support

For deployment issues:
1. Run `./validate.sh` to check prerequisites
2. Review CloudWatch Logs for errors
3. Check [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md) troubleshooting section
4. Verify AWS credentials and permissions

---

**Status:** ✅ Ready for Production Deployment

**Last Updated:** November 27, 2024

**Version:** 1.0.0
