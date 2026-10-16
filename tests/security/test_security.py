from src.core.security import (
    create_access_token,
    hash_password,
    verify_access_token,
    verify_password,
)


def test_password_hash_and_verify():
    password = "AIHub-Test-Password-2026"
    encoded = hash_password(password)

    assert encoded != password
    assert verify_password(password, encoded)
    assert not verify_password("Wrong-Password-2026", encoded)


def test_malformed_password_hash_is_rejected():
    assert not verify_password("Some-Password-2026", "not-a-valid-hash")


def test_valid_access_token(monkeypatch):
    monkeypatch.setenv(
        "AI_HUB_SECRET_KEY",
        "ai-hub-pytest-secret-key-at-least-32-characters",
    )

    token = create_access_token("test-user-001")
    payload = verify_access_token(token)

    assert payload is not None
    assert payload["sub"] == "test-user-001"


def test_tampered_access_token_is_rejected(monkeypatch):
    monkeypatch.setenv(
        "AI_HUB_SECRET_KEY",
        "ai-hub-pytest-secret-key-at-least-32-characters",
    )

    token = create_access_token("test-user-001")
    tampered = token + "tampered"

    assert verify_access_token(tampered) is None


def test_empty_and_malformed_tokens_are_rejected(monkeypatch):
    monkeypatch.setenv(
        "AI_HUB_SECRET_KEY",
        "ai-hub-pytest-secret-key-at-least-32-characters",
    )

    assert verify_access_token("") is None
    assert verify_access_token("not-a-token") is None
