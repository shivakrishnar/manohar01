"""Service to implement required archiving workflow described in the ticket.

- Finds clients (via ClientFetcher)
- Filters clients that have scope 'dex/trigger:all'
- For each client, obtains an OAuth token via TokenProvider (client credentials) if available
- Calls trigger endpoint for that client using TriggerFetcher
- Uploads the raw JSON response to S3 at key: trigger/<clientid>/<clientid>_trigger_yyyymmdd.json

Notes:
- Uses environment variables as fallback configuration:
  - BUCKET, PREFIX (for S3Uploader)
  - TRIGGER_BASE_URL if client doesn't have trigger_url
  - CLIENT_TOKEN_URL if client-specific token endpoint isn't provided

"""
import os
import json
import datetime
from typing import List, Dict, Any

from .client_fetcher import ClientFetcher
from .token_provider import TokenProvider
from .trigger.trigger_fetcher import TriggerFetcher
from .storage.s3_uploader import S3Uploader


class ArchiverLambdaService:
    def __init__(self, cfg: Dict[str, Any] | None = None):
        self.cfg = cfg or {}
        self.client_fetcher = ClientFetcher(self.cfg.get('client_fetch', {}))
        self.token_provider = TokenProvider(self.cfg.get('token', {}))

        bucket = os.environ.get('BUCKET') or self.cfg.get('bucket')
        if not bucket:
            raise RuntimeError('BUCKET must be configured (env or cfg)')
        prefix = os.environ.get('PREFIX', '') or self.cfg.get('prefix', '')
        self.uploader = S3Uploader({'bucket': bucket, 'prefix': prefix})

        self.trigger_base = os.environ.get('TRIGGER_BASE_URL') or self.cfg.get('trigger_base_url')
        self.client_token_url = os.environ.get('CLIENT_TOKEN_URL') or self.cfg.get('client_token_url')

    def _format_filename(self, client_id: str, dt: datetime.datetime) -> str:
        d = dt.strftime('%Y%m%d')
        return f"{client_id}_trigger_{d}.json"

    def run_once(self) -> Dict[str, Any]:
        clients = self.client_fetcher.get_clients()
        if not clients:
            return {'archived': []}

        results: List[Dict[str, Any]] = []
        today = datetime.datetime.utcnow()
        for c in clients:
            # Determine scopes list
            scopes = c.get('scopes') or c.get('scope') or []
            if isinstance(scopes, str):
                scopes = [scopes]
            if 'dex/trigger:all' not in scopes:
                # skip clients without required scope
                continue

            client_id = c.get('client_id') or c.get('ClientID') or c.get('oauth_client_id')
            if not client_id:
                # must have id
                continue

            # Determine trigger URL per client
            trigger_url = c.get('trigger_url') or (self.trigger_base.rstrip('/') + '/data-exchange/trigger' if self.trigger_base else None)
            if not trigger_url:
                # nothing to fetch
                continue

            # Obtain token if client credentials are present
            token = None
            oauth_id = c.get('oauth_client_id')
            oauth_secret = c.get('oauth_client_secret')
            token_url = c.get('token_url') or self.client_token_url
            if oauth_id and oauth_secret and token_url:
                try:
                    token = self.token_provider.get_token_for_client(oauth_id, oauth_secret, token_url, scope='dex/trigger:all')
                except Exception as e:
                    # log and skip
                    print(f"Token exchange failed for client {client_id}: {e}")
                    continue

            # Fetch triggers using TriggerFetcher
            fetcher = TriggerFetcher({'url': trigger_url, 'sample_count': 0})
            try:
                triggers = fetcher.fetch_triggers(token=token)
            except Exception as e:
                print(f"Fetching triggers failed for client {client_id}: {e}")
                continue

            # if response is list or single object, store raw JSON
            payload = triggers
            filename = self._format_filename(client_id, today)
            key = f"trigger/{client_id}/{filename}"
            data = json.dumps(payload, indent=2)
            try:
                s3_path = self.uploader.upload(key, data.encode('utf-8'))
                results.append({'client_id': client_id, 's3': s3_path, 'count': len(triggers) if isinstance(triggers, list) else 1})
            except Exception as e:
                print(f"Failed to upload triggers for {client_id}: {e}")
                continue

        return {'archived': results, 'count': len(results)}
*** End Patch