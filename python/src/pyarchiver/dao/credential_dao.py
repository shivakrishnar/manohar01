"""Credential DAO stub — would read secrets or encrypted credentials in production"""
from ..models.client_credential import ClientCredential


class CredentialDao:
    def __init__(self):
        self._credentials = {}

    def get_credential(self, client_id: str) -> ClientCredential | None:
        return self._credentials.get(client_id)

    def put_credential(self, cred: ClientCredential):
        self._credentials[cred.client_id] = cred
