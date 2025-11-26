"""Simple HTTP trigger fetcher; returns a list of trigger-like dicts.
This is intentionally minimal: it will either call a real endpoint or fall back to a
hard-coded sample for local testing.
"""
import requests


class TriggerFetcher:
    def __init__(self, cfg: dict):
        self.cfg = cfg or {}
        self.url = self.cfg.get('url')
        self.sample_count = int(self.cfg.get('sample_count', 2))

    def fetch_triggers(self):
        if self.url:
            print(f"Fetching triggers from {self.url}")
            try:
                resp = requests.get(self.url, timeout=10)
                resp.raise_for_status()
                data = resp.json()
                if isinstance(data, list):
                    return data
                return [data]
            except Exception as e:
                print(f"HTTP fetch failed: {e}")

        # fallback sample data
        return [
            {'id': f'sample-{i+1}', 'payload': {'message': 'Hello', 'index': i+1}}
            for i in range(self.sample_count)
        ]
