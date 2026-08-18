import datetime

import pytest

from api import (
    APIKeyRecord,
    DEFAULT_API_KEY_LIFETIME,
    api_key_directory,
    create_api_key,
    hash_api_key,
    revoke_api_key,
    validate_api_key,
)


CURRENT_TIME = datetime.datetime(2026, 8, 18, 10, 0, 0)


@pytest.fixture(autouse=True)
def clear_api_key_store() -> None:
    api_key_directory.api_keys_directory.clear()


def test_created_api_key_is_valid() -> None:
    api_key = create_api_key("user_40", current_time=CURRENT_TIME)

    assert validate_api_key(api_key, CURRENT_TIME) is True


def test_unknown_api_key_is_invalid() -> None:
    assert validate_api_key("bad_key", CURRENT_TIME) is False


def test_create_api_key_stores_api_key_record() -> None:
    api_key = create_api_key("user_40", current_time=CURRENT_TIME)

    assert api_key_directory.api_keys_directory[-1] == APIKeyRecord(
        hash_api_key(api_key),
        "user_40",
        CURRENT_TIME,
        CURRENT_TIME + DEFAULT_API_KEY_LIFETIME,
        False,
    )

def test_revoked_api_key_is_invalid() -> None:
    user_id = "21"
    api = "sk-revoked-user-21"
    api_key_record = APIKeyRecord(
        hash_api_key(api),
        user_id,
        CURRENT_TIME,
        CURRENT_TIME + DEFAULT_API_KEY_LIFETIME,
        True
    )
    api_key_directory.add_api_key(api_key_record)
    assert validate_api_key(api, CURRENT_TIME) is False


def test_revoke_api_key_toggle() -> None:
    api_key = create_api_key("21", current_time=CURRENT_TIME)
    revoke_api_key(api_key, "21")

    assert validate_api_key(api_key, CURRENT_TIME) is False    

def test_revoke_api_key_returns_true_when_key_is_revoked() -> None:
    api_key = create_api_key("21", current_time=CURRENT_TIME)
    assert revoke_api_key(api_key, "21") is True


def test_revoke_api_key_returns_false_for_wrong_user() -> None:
    api_key = create_api_key("user_40", current_time=CURRENT_TIME)

    assert revoke_api_key(api_key, "user_99") is False
    assert validate_api_key(api_key, CURRENT_TIME) is True


def test_create_api_key_generates_again_when_key_already_exists() -> None:
    existing_api_key = "sk-existing-user_40"
    api_key_directory.add_api_key(
        APIKeyRecord(
            hash_api_key(existing_api_key),
            "user_40",
            CURRENT_TIME,
            CURRENT_TIME + DEFAULT_API_KEY_LIFETIME,
            False,
        )
    )
    generated_keys = [existing_api_key, "sk-unique-user_40"]

    def fake_key_generator(user_id: str) -> str:
        return generated_keys.pop(0)

    api_key = create_api_key("user_40", fake_key_generator, CURRENT_TIME)

    assert api_key == "sk-unique-user_40"
    assert api_key_directory.find_record(hash_api_key("sk-unique-user_40")) == APIKeyRecord(
        hash_api_key("sk-unique-user_40"),
        "user_40",
        CURRENT_TIME,
        CURRENT_TIME + DEFAULT_API_KEY_LIFETIME,
        False,
    )


def test_create_api_key_does_not_store_raw_api_key() -> None:
    api_key = create_api_key("user_40", current_time=CURRENT_TIME)

    assert api_key_directory.api_keys_directory[-1].api_key_hash == hash_api_key(api_key)
    assert api_key_directory.api_keys_directory[-1].api_key_hash != api_key


def test_expired_api_key_is_invalid() -> None:
    api_key = create_api_key("user_40", current_time=CURRENT_TIME)
    after_expiry = CURRENT_TIME + DEFAULT_API_KEY_LIFETIME

    assert validate_api_key(api_key, after_expiry) is False
