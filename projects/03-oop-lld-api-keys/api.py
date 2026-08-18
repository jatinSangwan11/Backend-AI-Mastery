import datetime
from typing import Callable

from models import APIKeyDisplayRecord, APIKeyRecord, APIKeyValidationResult
from security import generate_api_key, hash_api_key
from store import api_key_directory

DEFAULT_API_KEY_LIFETIME = datetime.timedelta(days=30)

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
        for record in records
    ]


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
