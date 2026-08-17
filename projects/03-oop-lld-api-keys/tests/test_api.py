from api import APIKeyRecord, api_keys_directory, create_api_key, validate_api_key


def test_created_api_key_is_valid() -> None:
    api_key = create_api_key("user_40")

    assert validate_api_key(api_key) is True


def test_unknown_api_key_is_invalid() -> None:
    assert validate_api_key("bad_key") is False


def test_create_api_key_stores_api_key_record() -> None:
    api_key = create_api_key("user_40")

    assert api_keys_directory[-1] == APIKeyRecord(
        api_key,
        "user_40",
        "2026-08-17",
        False,
    )
