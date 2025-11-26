"""Token provider stub — handles simple token provider logic
In a full implementation this would fetch tokens from an OAuth server or local secrets store.
"""
import time


class TokenProvider:
    def __init__(self, cfg: dict):
        self.cfg = cfg or {}
        self.token = None
        self.expires_at = 0

    def get_token(self):
        if not self.token or time.time() > self.expires_at - 5:
            # refresh synthetically
            self.token = self.cfg.get('token', 'demo-token')
            self.expires_at = time.time() + 3600
        return self.token
