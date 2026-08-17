import random
from dataclasses import dataclass


@dataclass
class APIKeyRecord:
    api_key: str
    user_id: str
    created_at: str
    revoked: bool


api_keys_directory: list[APIKeyRecord] = []


def create_api_key(user: str) -> str:
    random_numeric = random.randint(0,1000)
    api = f"sk-{random_numeric}-{user}"

    api_key_record = APIKeyRecord(api, user, "2026-08-17", False)
    api_keys_directory.append(api_key_record)
    return api


def validate_api_key(api_key: str) -> bool:

    for api_key_record in api_keys_directory:
        if api_key_record.api_key == api_key:
            return True
    
    return False


if __name__ == "__main__":
    api_key = create_api_key("jatin")
    print(validate_api_key(api_key))
