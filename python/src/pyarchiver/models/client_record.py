from dataclasses import dataclass


@dataclass
class ClientRecord:
    client_id: str
    name: str | None = None
    state: str | None = None

    def to_dict(self):
        return {'client_id': self.client_id, 'name': self.name, 'state': self.state}
