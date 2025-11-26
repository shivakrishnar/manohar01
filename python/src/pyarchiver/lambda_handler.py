"""AWS Lambda handler for pyarchiver

Behavior:
- If event contains a `triggers` list -> those triggers will be archived
- Else the lambda will try to fetch triggers from TRIGGER_URL environment variable using TriggerFetcher
- Uploads each trigger as JSON into the S3 bucket defined by environment variable `BUCKET`
- Returns a run summary JSON

Design notes:
- Uses S3Uploader (which in Lambda will pick up IAM role credentials automatically)
- Keeps business logic minimal so unit tests can be added easily
"""
import os
import json
import logging
from typing import Any, Dict, List

from .trigger.trigger_fetcher import TriggerFetcher
from .storage.s3_uploader import S3Uploader
from .archiver_lambda_service import ArchiverLambdaService

logger = logging.getLogger("pyarchiver.lambda_handler")
logger.setLevel(os.environ.get("LOG_LEVEL", "INFO"))


def _get_triggers_from_event(event: Dict[str, Any]) -> List[Dict[str, Any]]:
    if not event:
        return []

    if "triggers" in event:
        if isinstance(event["triggers"], list):
            return event["triggers"]
        return [event["triggers"]]

    # Support direct single trigger payloads e.g. { "id": "abc", "payload": {...}}
    if isinstance(event, dict) and event.get("id"):
        return [event]

    return []


def handler(event: Dict[str, Any], context: Any = None) -> Dict[str, Any]:
    """Lambda handler entrypoint

    Environment variables expected / used:
    - BUCKET (required): S3 bucket name to upload JSON files
    - PREFIX (optional): S3 key prefix
    - TRIGGER_URL (optional): if no triggers in event then fetch from this URL
    """
    bucket = os.environ.get("BUCKET")
    prefix = os.environ.get("PREFIX", "")

    if not bucket:
        raise RuntimeError("Environment variable BUCKET must be set for Lambda to upload to S3")

    s3_cfg = {"bucket": bucket, "prefix": prefix}
    uploader = S3Uploader(s3_cfg)

    # If called with run_clients or action=run_clients, run the client-based archiver
    if event and (event.get('run_clients') or event.get('action') == 'run_clients'):
        svc = ArchiverLambdaService()
        return svc.run_once()

    # Otherwise, treat event as direct triggers or fetch a default trigger url
    triggers = _get_triggers_from_event(event)
    if not triggers:
        trigger_url = os.environ.get("TRIGGER_URL")
        if trigger_url:
            fetcher = TriggerFetcher({"url": trigger_url, "sample_count": 0})
            triggers = fetcher.fetch_triggers()
        else:
            # nothing to do
            logger.info("No triggers in event and no TRIGGER_URL configured. Exiting.")
            return {"archived": []}

    archived = []
    for t in triggers:
        # basic validation
        if not t.get("id"):
            logger.warning("Skipping trigger with missing id: %s", t)
            continue
        key_filename = f"trigger_{t['id']}.json"
        data = json.dumps(t, indent=2)
        path = uploader.upload(key_filename, data.encode("utf-8"))
        archived.append({"id": t["id"], "s3_path": path})
        logger.info("Archived trigger %s -> %s", t["id"], path)

    result = {"archived": archived, "count": len(archived)}
    return result
