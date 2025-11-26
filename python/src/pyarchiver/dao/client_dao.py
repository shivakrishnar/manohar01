"""In-memory DAO for demonstration — mirrors the Java ClientDao minimal behavior"""
from typing import Dict
from ..models.client_record import ClientRecord


class ClientDao:
    def __init__(self):
        self._store: Dict[str, ClientRecord] = {}

    def get_client(self, client_id: str) -> ClientRecord | None:
        return self._store.get(client_id)

    def put_client(self, rec: ClientRecord):
        self._store[rec.client_id] = rec

    def all_clients(self):
        return list(self._store.values())
