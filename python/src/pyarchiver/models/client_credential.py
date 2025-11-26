from dataclasses import dataclass


@dataclass
class ClientCredential:
    client_id: str
    secret: str

    def __repr__(self):
        return f"ClientCredential(client_id={self.client_id!r}, secret=***hidden***)"
