import datetime
from dataclasses import dataclass


@dataclass
class APIKeyRecord:
    key_id: str
    api_key_hash: str
    user_id: str
    created_at: datetime.datetime
    expires_at: datetime.datetime
    revoked: bool


@dataclass
class APIKeyValidationResult:
    is_valid: bool
    user_id: str | None


@dataclass
class APIKeyDisplayRecord:
    key_id: str
    user_id: str
    created_at: datetime.datetime
    expires_at: datetime.datetime
    revoked: bool
