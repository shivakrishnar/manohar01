"""
DEX-API Trigger Response Archive Lambda Function

This Lambda function archives DEX-API trigger file responses to S3.
It fetches clients with dex-api scope (dex/trigger:all), makes API calls
to /data-exchange/trigger endpoint, and saves responses to S3.

Triggered by: Manual invocation, EventBridge, Step Functions, or other AWS services
AWS Services: Lambda, S3, RDS (SQL Server), Secrets Manager
"""

import json
import boto3
import os
import pymssql
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import logging
import requests
from botocore.exceptions import ClientError

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Initialize AWS clients
s3_client = boto3.client('s3')
secrets_client = boto3.client('secretsmanager')

# Environment variables
S3_BUCKET = os.environ.get('S3_BUCKET_NAME')
DB_SECRET_NAME = os.environ.get('DB_SECRET_NAME')
API_SECRET_NAME = os.environ.get('API_SECRET_NAME')
DEX_API_BASE_URL = os.environ.get('DEX_API_BASE_URL')
TRIGGER_DATE_OFFSET_DAYS = int(os.environ.get('TRIGGER_DATE_OFFSET_DAYS', '0'))


def get_secret(secret_name: str) -> Dict:
    """
    Retrieve secret from AWS Secrets Manager
    
    Args:
        secret_name: Name of the secret in Secrets Manager
        
    Returns:
        Dictionary containing secret values
    """
    try:
        response = secrets_client.get_secret_value(SecretId=secret_name)
        return json.loads(response['SecretString'])
    except ClientError as e:
        logger.error(f"Error retrieving secret {secret_name}: {e}")
        raise


def get_database_connection():
    """
    Establish connection to SQL Server database
    
    Returns:
        pymssql connection object
    """
    try:
        db_credentials = get_secret(DB_SECRET_NAME)
        
        conn = pymssql.connect(
            server=db_credentials['host'],
            user=db_credentials['username'],
            password=db_credentials['password'],
            database=db_credentials.get('database', 'Mediant'),
            port=db_credentials.get('port', 1433)
        )
        
        logger.info("Successfully connected to database")
        return conn
        
    except Exception as e:
        logger.error(f"Database connection error: {e}")
        raise


def get_clients_with_dex_trigger_scope() -> List[Dict]:
    """
    Query database to get list of clients with dex-api scope: dex/trigger:all
    
    SQL Query:
    SELECT DISTINCT c.ClientID, c.name 
    FROM Client c
    INNER JOIN ClientServiceExt cs ON c.ClientID = cs.ClientID 
    WHERE c.OAuth2ClientCredentialsID IS NOT NULL
    AND cs.ServiceID IN (2,8,3,4,5)
    
    Returns:
        List of dictionaries containing ClientID and name
    """
    conn = None
    try:
        conn = get_database_connection()
        cursor = conn.cursor(as_dict=True)
        
        query = """
        SELECT DISTINCT c.ClientID, c.name 
        FROM Client c
        INNER JOIN ClientServiceExt cs ON c.ClientID = cs.ClientID 
        WHERE c.OAuth2ClientCredentialsID IS NOT NULL
        AND cs.ServiceID IN (2,8,3,4,5)
        """
        
        cursor.execute(query)
        clients = cursor.fetchall()
        
        logger.info(f"Retrieved {len(clients)} clients with dex-api trigger scope")
        return clients
        
    except Exception as e:
        logger.error(f"Error querying clients: {e}")
        raise
    finally:
        if conn:
            conn.close()


def get_api_access_token() -> str:
    """
    Get OAuth2 access token for DEX-API authentication
    
    Returns:
        Access token string
    """
    try:
        api_credentials = get_secret(API_SECRET_NAME)
        
        # Adjust this based on your OAuth2 implementation
        token_url = api_credentials.get('token_url')
        client_id = api_credentials.get('client_id')
        client_secret = api_credentials.get('client_secret')
        
        response = requests.post(
            token_url,
            data={
                'grant_type': 'client_credentials',
                'client_id': client_id,
                'client_secret': client_secret,
                'scope': 'dex/trigger:all'
            },
            headers={'Content-Type': 'application/x-www-form-urlencoded'}
        )
        
        response.raise_for_status()
        token_data = response.json()
        
        return token_data['access_token']
        
    except Exception as e:
        logger.error(f"Error obtaining access token: {e}")
        raise


def fetch_trigger_data(client_id: int, access_token: str, trigger_date: str) -> Optional[Dict]:
    """
    Make API call to /data-exchange/trigger endpoint for specific client
    
    Args:
        client_id: Client ID to fetch trigger data for
        access_token: OAuth2 access token
        trigger_date: Date for trigger file (YYYY-MM-DD format)
        
    Returns:
        API response as dictionary, or None if request fails
    """
    try:
        url = f"{DEX_API_BASE_URL}/data-exchange/trigger"
        
        headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json'
        }
        
        params = {
            'clientId': client_id,
            'triggerDate': trigger_date
        }
        
        response = requests.get(url, headers=headers, params=params, timeout=30)
        response.raise_for_status()
        
        logger.info(f"Successfully fetched trigger data for client {client_id}")
        return response.json()
        
    except requests.exceptions.RequestException as e:
        logger.error(f"Error fetching trigger data for client {client_id}: {e}")
        return None


def upload_to_s3(client_id: int, trigger_data: Dict, trigger_date: str) -> bool:
    """
    Upload trigger response data to S3
    
    S3 folder structure: trigger/[clientid]/file
    File name format: clientid_trigger_yyyymmdd
    
    Args:
        client_id: Client ID
        trigger_data: Trigger response data
        trigger_date: Trigger date (YYYY-MM-DD format)
        
    Returns:
        True if upload successful, False otherwise
    """
    try:
        # Format date for filename (yyyymmdd)
        date_obj = datetime.strptime(trigger_date, '%Y-%m-%d')
        formatted_date = date_obj.strftime('%Y%m%d')
        
        # Construct S3 key
        s3_key = f"trigger/{client_id}/{client_id}_trigger_{formatted_date}.json"
        
        # Convert data to JSON string
        json_data = json.dumps(trigger_data, indent=2)
        
        # Upload to S3
        s3_client.put_object(
            Bucket=S3_BUCKET,
            Key=s3_key,
            Body=json_data.encode('utf-8'),
            ContentType='application/json',
            Metadata={
                'client_id': str(client_id),
                'trigger_date': trigger_date,
                'archived_at': datetime.utcnow().isoformat()
            }
        )
        
        logger.info(f"Successfully uploaded trigger data to s3://{S3_BUCKET}/{s3_key}")
        return True
        
    except ClientError as e:
        logger.error(f"Error uploading to S3 for client {client_id}: {e}")
        return False


def lambda_handler(event, context):
    """
    Main Lambda handler function
    
    Args:
        event: EventBridge event (scheduled trigger)
        context: Lambda context object
        
    Returns:
        Response dictionary with status and results
    """
    logger.info("Starting DEX-API Trigger Response Archive process")
    logger.info(f"Event: {json.dumps(event)}")
    
    results = {
        'total_clients': 0,
        'successful_archives': 0,
        'failed_archives': 0,
        'errors': []
    }
    
    try:
        # Validate environment variables
        required_vars = ['S3_BUCKET_NAME', 'DB_SECRET_NAME', 'API_SECRET_NAME', 'DEX_API_BASE_URL']
        missing_vars = [var for var in required_vars if not os.environ.get(var)]
        
        if missing_vars:
            raise ValueError(f"Missing required environment variables: {', '.join(missing_vars)}")
        
        # Calculate trigger date (typically current date or offset)
        trigger_date = (datetime.now() + timedelta(days=TRIGGER_DATE_OFFSET_DAYS)).strftime('%Y-%m-%d')
        logger.info(f"Processing trigger data for date: {trigger_date}")
        
        # Get OAuth2 access token
        access_token = get_api_access_token()
        
        # Get list of clients with dex-api trigger scope
        clients = get_clients_with_dex_trigger_scope()
        results['total_clients'] = len(clients)
        
        if not clients:
            logger.warning("No clients found with dex-api trigger scope")
            return {
                'statusCode': 200,
                'body': json.dumps(results)
            }
        
        # Process each client
        for client in clients:
            client_id = client['ClientID']
            client_name = client['name']
            
            logger.info(f"Processing client: {client_id} ({client_name})")
            
            try:
                # Fetch trigger data from API
                trigger_data = fetch_trigger_data(client_id, access_token, trigger_date)
                
                if trigger_data is None:
                    results['failed_archives'] += 1
                    results['errors'].append({
                        'client_id': client_id,
                        'client_name': client_name,
                        'error': 'Failed to fetch trigger data from API'
                    })
                    continue
                
                # Upload to S3
                upload_success = upload_to_s3(client_id, trigger_data, trigger_date)
                
                if upload_success:
                    results['successful_archives'] += 1
                else:
                    results['failed_archives'] += 1
                    results['errors'].append({
                        'client_id': client_id,
                        'client_name': client_name,
                        'error': 'Failed to upload to S3'
                    })
                    
            except Exception as e:
                logger.error(f"Error processing client {client_id}: {e}")
                results['failed_archives'] += 1
                results['errors'].append({
                    'client_id': client_id,
                    'client_name': client_name,
                    'error': str(e)
                })
        
        # Log summary
        logger.info(f"Archive process completed. Results: {json.dumps(results)}")
        
        return {
            'statusCode': 200,
            'body': json.dumps(results)
        }
        
    except Exception as e:
        logger.error(f"Fatal error in lambda_handler: {e}")
        return {
            'statusCode': 500,
            'body': json.dumps({
                'error': str(e),
                'results': results
            })
        }
