"""Basic S3 uploader wrapper using boto3. If boto3 is not configured it provides a helpful message."""
import os

try:
    import boto3
    from botocore.exceptions import BotoCoreError, ClientError
except Exception:  # pragma: no cover - optional dependency
    boto3 = None


class S3Uploader:
    def __init__(self, cfg: dict):
        self.bucket = cfg.get('bucket')
        self.prefix = cfg.get('prefix', '')
        if boto3 is None:
            print('boto3 not available — S3Uploader will not function until boto3 is installed')
            self.client = None
        else:
            self.client = boto3.client('s3')

    def upload(self, filename: str, data: bytes) -> str:
        if not self.client:
            raise RuntimeError('S3 client not configured (boto3 missing or not initialized)')
        key = f"{self.prefix.rstrip('/')}/{filename}" if self.prefix else filename
        try:
            self.client.put_object(Bucket=self.bucket, Key=key, Body=data)
            return f"s3://{self.bucket}/{key}"
        except (BotoCoreError, ClientError) as e:
            raise
