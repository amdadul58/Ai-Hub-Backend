"""Environment variable parsing helpers."""

import os


def get_env(name, default=None):
    """Return a trimmed environment value or its default."""
    value = os.getenv(name)
    if value is None:
        return default
    return value.strip()


def get_bool(name, default=False):
    """Parse a boolean environment variable safely."""
    value = os.getenv(name)
    if value is None:
        return default

    normalized = value.strip().lower()
    if normalized in {"1", "true", "yes", "on"}:
        return True
    if normalized in {"0", "false", "no", "off"}:
        return False

    raise ValueError(f"Invalid boolean value for {name}.")


def get_int(name, default, *, minimum=None, maximum=None):
    """Parse and optionally range-check an integer environment variable."""
    value = os.getenv(name)
    if value is None:
        result = default
    else:
        try:
            result = int(value.strip())
        except (ValueError, AttributeError) as exc:
            raise ValueError(f"Invalid integer value for {name}.") from exc

    if minimum is not None and result < minimum:
        raise ValueError(f"{name} must be at least {minimum}.")
    if maximum is not None and result > maximum:
        raise ValueError(f"{name} must be at most {maximum}.")

    return result
