# Secrets Manager Setup Guide

This document provides the exact JSON structure needed for AWS Secrets Manager secrets.

## Database Credentials Secret

**Secret Name:** `dex-archive/db-credentials`

**JSON Structure:**
```json
{
  "host": "your-sql-server-endpoint.rds.amazonaws.com",
  "username": "your_database_username",
  "password": "your_database_password",
  "database": "Mediant",
  "port": 1433
}
```

**AWS CLI Command to Create:**
```bash
aws secretsmanager create-secret \
    --name dex-archive/db-credentials \
    --description "Database credentials for DEX Trigger Archive" \
    --secret-string '{
      "host": "your-sql-server-endpoint.rds.amazonaws.com",
      "username": "your_database_username",
      "password": "your_database_password",
      "database": "Mediant",
      "port": 1433
    }'
```

---

## API Credentials Secret

**Secret Name:** `dex-archive/api-credentials`

**JSON Structure:**
```json
{
  "token_url": "https://your-oauth-server.com/oauth/token",
  "client_id": "your_oauth_client_id",
  "client_secret": "your_oauth_client_secret"
}
```

**AWS CLI Command to Create:**
```bash
aws secretsmanager create-secret \
    --name dex-archive/api-credentials \
    --description "API OAuth2 credentials for DEX API" \
    --secret-string '{
      "token_url": "https://your-oauth-server.com/oauth/token",
      "client_id": "your_oauth_client_id",
      "client_secret": "your_oauth_client_secret"
    }'
```

---

## Update Existing Secret

If you need to update an existing secret:

```bash
aws secretsmanager update-secret \
    --secret-id dex-archive/db-credentials \
    --secret-string '{
      "host": "new-endpoint.rds.amazonaws.com",
      "username": "new_username",
      "password": "new_password",
      "database": "Mediant",
      "port": 1433
    }'
```

---

## Verify Secret Creation

```bash
# List all secrets
aws secretsmanager list-secrets

# Get specific secret value
aws secretsmanager get-secret-value --secret-id dex-archive/db-credentials
aws secretsmanager get-secret-value --secret-id dex-archive/api-credentials
```
