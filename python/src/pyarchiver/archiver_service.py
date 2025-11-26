"""Core orchestration: fetch triggers, validate and upload"""
import os
import json
from .trigger.trigger_fetcher import TriggerFetcher
from .storage.local_uploader import LocalUploader
from .storage.s3_uploader import S3Uploader


class ArchiverService:
    def __init__(self, cfg: dict):
        self.cfg = cfg or {}
        self.fetcher = TriggerFetcher(self.cfg.get('api', {}))
        storage_cfg = self.cfg.get('storage', {})
        if storage_cfg.get('type') == 's3':
            self.uploader = S3Uploader(storage_cfg)
        else:
            self.uploader = LocalUploader(storage_cfg)

    def run_once(self):
        """Perform one fetch/process/upload cycle"""
        triggers = self.fetcher.fetch_triggers()
        print(f"Found {len(triggers)} triggers to archive")
        archived = []
        for t in triggers:
            # validate minimal fields
            if not t.get('id'):
                print(f"Skipping trigger with missing id: {t}")
                continue
            filename = f"trigger_{t['id']}.json"
            data = json.dumps(t, indent=2)
            path = self.uploader.upload(filename, data.encode('utf-8'))
            archived.append({'id': t['id'], 'path': path})
            print(f"Archived trigger {t['id']} -> {path}")

        # Save a run summary
        out = {
            'project': os.path.basename(os.getcwd()),
            'archived': archived,
        }
        out_file = os.path.join(self.cfg.get('output', '.'), 'last_run_summary.json')
        os.makedirs(os.path.dirname(out_file) or '.', exist_ok=True)
        with open(out_file, 'w') as f:
            json.dump(out, f, indent=2)
        print(f"Wrote summary to {out_file}")
        return out
