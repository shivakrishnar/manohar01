"""Write bytes to a local directory (default ./archives)"""
import os


class LocalUploader:
    def __init__(self, cfg: dict):
        self.dir = cfg.get('local_dir', './archives')
        os.makedirs(self.dir, exist_ok=True)

    def upload(self, filename: str, data: bytes) -> str:
        path = os.path.join(self.dir, filename)
        parent = os.path.dirname(path)
        if parent:
            os.makedirs(parent, exist_ok=True)
        with open(path, 'wb') as f:
            f.write(data)
        return os.path.abspath(path)
