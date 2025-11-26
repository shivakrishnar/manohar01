# Constants used by trigger handling

ApiSecurityScopes = {
    'read': 'trigger:read',
    'write': 'trigger:write',
}

Columns = ['id', 'payload', 'timestamp']

ValidationValues = {
    'allowed_states': ['NEW', 'PROCESSED'],
}

SQLErrorCode = {
    'deadlock': 1205,
    'duplicate_key': 2601
}
