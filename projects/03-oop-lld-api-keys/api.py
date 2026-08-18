import hashlib
from dataclasses import dataclass
from typing import Callable
import secrets
import datetime

DEFAULT_API_KEY_LIFETIME = datetime.timedelta(days=30)


@dataclass
class APIKeyRecord:
    api_key_hash: str
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
        

api_key_directory = APIKeyStore()
# api_keys_directory: list[APIKeyRecord] = []

def revoke_api_key(api_key: str, user_id: str) -> bool:
    api_key_hash = hash_api_key(api_key)
    record = api_key_directory.find_record(api_key_hash)
    if record and record.user_id == user_id: 
        record.revoked = True
        return True
        
    return False

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
        api_key_hash,
        user,
        current_time,
        current_time + DEFAULT_API_KEY_LIFETIME,
        False,
    )
    
    api_key_directory.add_api_key(api_key_record)
    return api_key


def validate_api_key(api_key: str, current_time: datetime.datetime | None = None) -> bool:
    if current_time is None:
        current_time = datetime.datetime.now()

    api_key_hash = hash_api_key(api_key)
    record = api_key_directory.find_record(api_key_hash)
    if record and record.revoked == False and current_time < record.expires_at:
        return True

    return False


if __name__ == "__main__":
    api_key = create_api_key("jatin")
    print(validate_api_key(api_key))
