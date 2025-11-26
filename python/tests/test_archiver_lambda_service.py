import os
import shutil
import json
import tempfile
from pyarchiver.archiver_lambda_service import ArchiverLambdaService


def test_archiver_local_archive(tmp_path, monkeypatch):
    # Prepare temp local bucket path
    bucket = str(tmp_path / "bucket")
    os.makedirs(bucket, exist_ok=True)

    # Build minimal config with a client that has no trigger_url but sample_count >0
    cfg = {
        'api': {'sample_count': 2},
        'client_fetch': {
            'clients': [
                {
                    'client_id': 'sample-client-1',
                    'name': 'Sample Client 1',
                    'scopes': ['dex/trigger:all']
                }
            ]
        },
        'bucket': bucket,
        'prefix': 'trigger'
    }

    svc = ArchiverLambdaService(cfg)
    result = svc.run_once()

    # Expect at least one archived entry
    assert 'archived' in result
    assert result['count'] >= 1

    # Check file exists in the local bucket/prefix
    # Example path: <bucket>/trigger/sample-client-1/sample-client-1_trigger_YYYYMMDD.json
    archived = result['archived']
    assert len(archived) > 0
    first = archived[0]
    s3path = first['s3']
    # s3path is a local file path when using the local uploader
    assert s3path.startswith(os.path.abspath(bucket))
    assert os.path.exists(s3path)


 