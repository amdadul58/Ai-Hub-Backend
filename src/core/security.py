import base64
import binascii
import hashlib
import hmac
import json
import os
import secrets
import time


_PASSWORD_ALGORITHM = "pbkdf2_sha256"
_PASSWORD_ROUNDS = 310000
_MIN_SECRET_LENGTH = 32
_MAX_TOKEN_LENGTH = 8192


def hash_password(password):
    if not isinstance(password, str) or not 8 <= len(password) <= 128:
        raise ValueError("Password must contain 8 to 128 characters.")

    salt = secrets.token_bytes(16)
    derived = hashlib.pbkdf2_hmac(
        "sha256", password.encode("utf-8"), salt, _PASSWORD_ROUNDS
    )
    return "{}${}${}${}".format(
        _PASSWORD_ALGORITHM,
        _PASSWORD_ROUNDS,
        base64.urlsafe_b64encode(salt).decode("ascii"),
        base64.urlsafe_b64encode(derived).decode("ascii"),
    )


def verify_password(password, encoded):
    try:
        if not isinstance(password, str) or not isinstance(encoded, str):
            return False

        algorithm, rounds_text, salt_text, hash_text = encoded.split("$", 3)
        if algorithm != _PASSWORD_ALGORITHM:
            return False

        rounds = int(rounds_text)
        if not 100000 <= rounds <= 1000000:
            return False

        salt = base64.b64decode(
            salt_text.encode("ascii"), altchars=b"-_", validate=True
        )
        expected = base64.b64decode(
            hash_text.encode("ascii"), altchars=b"-_", validate=True
        )

        if len(salt) != 16 or len(expected) != 32:
            return False

        actual = hashlib.pbkdf2_hmac(
            "sha256", password.encode("utf-8"), salt, rounds
        )
        return hmac.compare_digest(actual, expected)
    except (ValueError, TypeError, AttributeError, UnicodeError, binascii.Error):
        return False


def _secret():
    secret = os.getenv("AI_HUB_SECRET_KEY", "")
    if not isinstance(secret, str) or len(secret) < _MIN_SECRET_LENGTH:
        raise RuntimeError(
            "Set AI_HUB_SECRET_KEY to a random secret of at least 32 characters."
        )
    return secret.encode("utf-8")


def create_access_token(subject, expires_in=3600):
    if subject is None or not str(subject).strip():
        raise ValueError("A non-empty subject is required.")

    if isinstance(expires_in, bool) or not isinstance(expires_in, (int, float)):
        raise ValueError("expires_in must be a positive number.")

    if not 1 <= expires_in <= 604800:
        raise ValueError("expires_in must be between 1 second and 7 days.")

    now = int(time.time())
    payload = {
        "sub": str(subject),
        "iat": now,
        "exp": now + int(expires_in),
    }

    body = base64.urlsafe_b64encode(
        json.dumps(payload, separators=(",", ":")).encode("utf-8")
    ).decode("ascii").rstrip("=")

    signature = hmac.new(_secret(), body.encode("ascii"), hashlib.sha256).digest()
    signed = base64.urlsafe_b64encode(signature).decode("ascii").rstrip("=")
    return body + "." + signed


def verify_access_token(token):
    try:
        if not isinstance(token, str) or not token or len(token) > _MAX_TOKEN_LENGTH:
            return None

        parts = token.split(".")
        if len(parts) != 2:
            return None

        body, supplied_signature = parts
        if not body or not supplied_signature:
            return None

        expected_signature = base64.urlsafe_b64encode(
            hmac.new(_secret(), body.encode("ascii"), hashlib.sha256).digest()
        ).decode("ascii").rstrip("=")

        if not hmac.compare_digest(supplied_signature, expected_signature):
            return None

        decoded = base64.b64decode(
            (body + "=" * (-len(body) % 4)).encode("ascii"),
            altchars=b"-_",
            validate=True,
        )
        payload = json.loads(decoded.decode("utf-8"))

        if not isinstance(payload, dict):
            return None

        subject = payload.get("sub")
        issued_at = payload.get("iat")
        expires_at = payload.get("exp")
        now = int(time.time())

        if not isinstance(subject, str) or not subject.strip():
            return None

        if (
            isinstance(issued_at, bool)
            or not isinstance(issued_at, int)
            or issued_at > now + 60
        ):
            return None

        if (
            isinstance(expires_at, bool)
            or not isinstance(expires_at, int)
            or expires_at <= now
            or expires_at <= issued_at
        ):
            return None

        return payload

    except (
        ValueError,
        TypeError,
        KeyError,
        AttributeError,
        UnicodeError,
        binascii.Error,
        OverflowError,
        RecursionError,
    ):
        return None
