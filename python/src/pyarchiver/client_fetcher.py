"""Fetch clients to process for the archiver

Behavior:
- If environment CLIENTS_API_URL is set, GET that URL and expect JSON list of clients
- Else, read supplied clients from provided config dict (key 'clients')

Expected client shape (dict):
{
  "client_id": "123",
  "name": "Acme",
  "oauth_client_id": "abc",
  "oauth_client_secret": "secret",
  "scopes": ["dex/trigger:all"]
}

"""
import os
import requests
from typing import List, Dict, Any


class ClientFetcher:
    def __init__(self, cfg: Dict[str, Any] | None = None):
        self.cfg = cfg or {}
        self.api_url = os.environ.get('CLIENTS_API_URL') or self.cfg.get('clients_api_url')

    def get_clients(self) -> List[Dict[str, Any]]:
        if self.api_url:
            print(f"Fetching client list from {self.api_url}")
            r = requests.get(self.api_url, timeout=10)
            r.raise_for_status()
            data = r.json()
            if isinstance(data, list):
                return data
            return [data]

        # fallback to config
        return self.cfg.get('clients', [])
*** End Patch