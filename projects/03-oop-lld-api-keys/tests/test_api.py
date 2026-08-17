from api import APIKeyRecord, api_key_directory, create_api_key, revoke_api_key, validate_api_key


def test_created_api_key_is_valid() -> None:
    api_key = create_api_key("user_40")

    assert validate_api_key(api_key) is True


def test_unknown_api_key_is_invalid() -> None:
    assert validate_api_key("bad_key") is False


def test_create_api_key_stores_api_key_record() -> None:
    api_key = create_api_key("user_40")

    assert api_key_directory.api_keys_directory[-1] == APIKeyRecord(
        api_key,
        "user_40",
        "2026-08-17",
        False,
    )

def test_revoked_api_key_is_invalid() -> None:
    user_id = "21"
    api = "sk-revoked-user-21"
    api_key_record = APIKeyRecord(
        api,
        user_id,
        "2026-08-17",
        True
    )
    api_key_directory.add_api_key(api_key_record)
    assert validate_api_key(api) is False


def test_revoke_api_key_toggle() -> None:
    api_key = create_api_key("21")
    revoke_api_key(api_key, "21")

    assert validate_api_key(api_key) is False    

def test_revoke_api_key_returns_true_when_key_is_revoked() -> None:
    api_key = create_api_key("21")
    assert revoke_api_key(api_key, "21") is True


def test_revoke_api_key_returns_false_for_wrong_user() -> None:
    api_key = create_api_key("user_40")

    assert revoke_api_key(api_key, "user_99") is False
    assert validate_api_key(api_key) is True


def test_create_api_key_generates_again_when_key_already_exists() -> None:
    existing_api_key = "sk-existing-user_40"
    api_key_directory.add_api_key(
        APIKeyRecord(existing_api_key, "user_40", "2026-08-17", False)
    )
    generated_keys = [existing_api_key, "sk-unique-user_40"]

    def fake_key_generator(user_id: str) -> str:
        return generated_keys.pop(0)

    api_key = create_api_key("user_40", fake_key_generator)

    assert api_key == "sk-unique-user_40"
    assert api_key_directory.find_record("sk-unique-user_40") == APIKeyRecord(
        "sk-unique-user_40",
        "user_40",
        "2026-08-17",
        False,
    )
