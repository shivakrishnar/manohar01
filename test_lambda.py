"""
Test script for DEX Trigger Response Archive Lambda Function
Run this locally to validate function logic before deployment
"""

import json
import os
from lambda_function import lambda_handler

def test_lambda_locally():
    """
    Test the Lambda function locally with mock event
    
    Note: Requires valid AWS credentials and connectivity to:
    - AWS Secrets Manager
    - SQL Server database
    - DEX API endpoint
    - S3 bucket
    """
    
    # Set environment variables for testing
    os.environ['S3_BUCKET_NAME'] = 'dex-trigger-archive'
    os.environ['DB_SECRET_NAME'] = 'dex-archive/db-credentials'
    os.environ['API_SECRET_NAME'] = 'dex-archive/api-credentials'
    os.environ['DEX_API_BASE_URL'] = 'https://api.example.com'
    os.environ['TRIGGER_DATE_OFFSET_DAYS'] = '0'
    
    # Mock event (empty for this Lambda)
    event = {}
    
    # Mock context
    class MockContext:
        function_name = 'dex-trigger-response-archive'
        memory_limit_in_mb = 512
        invoked_function_arn = 'arn:aws:lambda:us-east-1:123456789012:function:dex-trigger-response-archive'
        aws_request_id = 'test-request-id'
    
    context = MockContext()
    
    print("Testing Lambda function locally...")
    print("=" * 50)
    
    try:
        response = lambda_handler(event, context)
        print("\nFunction Response:")
        print(json.dumps(response, indent=2))
        
        if response.get('statusCode') == 200:
            print("\n✓ Function executed successfully!")
        else:
            print(f"\n✗ Function failed with status code: {response.get('statusCode')}")
            
    except Exception as e:
        print(f"\n✗ Function raised exception: {e}")
        raise

if __name__ == '__main__':
    test_lambda_locally()
