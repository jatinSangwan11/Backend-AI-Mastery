import hashlib
from dataclasses import dataclass
from typing import Callable
import secrets
import datetime

DEFAULT_API_KEY_LIFETIME = datetime.timedelta(days=30)


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


class APIKeyStore:

    api_keys_directory: list[APIKeyRecord]

    def __init__(self) -> None:
        self.api_keys_directory = []

    def add_api_key(self, api_key_record: APIKeyRecord) -> str:
        self.api_keys_directory.append(api_key_record)
        return api_key_record.api_key_hash

    def find_record(self, api_key_hash: str) -> APIKeyRecord | None:
        for api_key_record in self.api_keys_directory:
            if api_key_hash == api_key_record.api_key_hash:
                return api_key_record

        return None

    def find_records_for_user(self, user_id: str) -> list[APIKeyRecord]:
        return [
            api_key_record
            for api_key_record in self.api_keys_directory
            if api_key_record.user_id == user_id
        ]
    
    def find_record_by_key_id(self, key_id: str) -> APIKeyRecord | None:
        for api_key_record in self.api_keys_directory:
            if api_key_record.key_id == key_id:
                return api_key_record
        
        return None
        

api_key_directory = APIKeyStore()
# api_keys_directory: list[APIKeyRecord] = []

def revoke_api_key(key_id: str, user_id: str) -> bool:
    record = api_key_directory.find_record_by_key_id(key_id)
    if record and record.user_id == user_id: 
        record.revoked = True
        return True
        
    return False


def list_api_keys(user_id: str) -> list[APIKeyDisplayRecord]:
    records = api_key_directory.find_records_for_user(user_id)
    return [
        APIKeyDisplayRecord(
            record.key_id,
            record.user_id,
            record.created_at,
            record.expires_at,
            record.revoked,
        )
        for record in records]


def generate_api_key(user_id: str) -> str:
    return f"sk-{secrets.token_urlsafe(32)}"


def hash_api_key(api_key: str) -> str:
    return hashlib.sha256(api_key.encode()).hexdigest()


def create_api_key(
    user: str,
    key_generator: Callable[[str], str] = generate_api_key,
    current_time: datetime.datetime | None = None,
) -> str:
    if current_time is None:
        current_time = datetime.datetime.now()

    while True:
        # Key generation is injectable so tests can force collisions without relying on random.
        api_key = key_generator(user)
        api_key_hash = hash_api_key(api_key)
        
        if api_key_directory.find_record(api_key_hash) is None:
            break

    api_key_record = APIKeyRecord(
        key_id=str(len(api_key_directory.api_keys_directory) + 1),
        api_key_hash=api_key_hash,
        user_id=user,
        created_at=current_time,
        expires_at=current_time + DEFAULT_API_KEY_LIFETIME,
        revoked=False,
    )
    
    api_key_directory.add_api_key(api_key_record)
    return api_key


def validate_api_key(
    api_key: str,
    current_time: datetime.datetime | None = None,
) -> APIKeyValidationResult:
    if current_time is None:
        current_time = datetime.datetime.now()

    api_key_hash = hash_api_key(api_key)
    record = api_key_directory.find_record(api_key_hash)
    if record and record.revoked == False and current_time < record.expires_at:
        return APIKeyValidationResult(True, record.user_id)

    return APIKeyValidationResult(False, None)


if __name__ == "__main__":
    api_key = create_api_key("jatin")
    print(validate_api_key(api_key))
