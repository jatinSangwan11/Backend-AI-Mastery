from models import APIKeyRecord


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
