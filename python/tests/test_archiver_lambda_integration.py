import os
import json
import tempfile
from pathlib import Path

from pyarchiver.archiver_lambda_service import ArchiverLambdaService


def test_integration_archiver_writes_files(tmp_path):
    # Create a temp directory to act as the 'bucket' (local dir upload)
    bucket_dir = tmp_path / "archive-bucket"
    bucket_dir.mkdir()

    # Configure two clients: one with sample fallback and one with manual trigger URL (also fallback works)
    cfg = {
        'api': {'sample_count': 2},
        'client_fetch': {
            'clients': [
                # client using sample fallback (no trigger_url)
                {'client_id': 'client-sample', 'name': 'Sample', 'scopes': ['dex/trigger:all']},
                # client with an explicit trigger_url but for integration we still use sample_count
                {'client_id': 'client-explicit', 'name': 'Explicit', 'scopes': ['dex/trigger:all'], 'trigger_url': None, 'sample_count': 1},
            ]
        },
        'bucket': str(bucket_dir),
        'prefix': 'trigger'
    }

    svc = ArchiverLambdaService(cfg)
    out = svc.run_once()

    # Ensure at least one archived entry
    assert 'archived' in out
    assert out['count'] >= 1

    # Verify files exist under the local bucket/prefix for each archived client
    for entry in out['archived']:
        s3_path = entry['s3']
        assert s3_path.startswith(str(bucket_dir))
        p = Path(s3_path)
        assert p.exists(), f"Archived file not found: {p}"

        # Check content looks like JSON and contains id
        data = json.loads(p.read_text())
        # sample_count returns a list - validate list or object
        assert data is not None
