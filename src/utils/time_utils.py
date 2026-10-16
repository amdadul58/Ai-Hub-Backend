from datetime import datetime, timezone


def utc_now():
    """Return the current timezone-aware UTC datetime."""
    return datetime.now(timezone.utc)


def utc_timestamp():
    """Return the current UTC time as an ISO-8601 string."""
    return utc_now().isoformat()


def elapsed_seconds(start, end=None):
    """Calculate elapsed seconds between datetime values."""
    end = end or utc_now()
    if start.tzinfo is None or end.tzinfo is None:
        raise ValueError("Both datetimes must be timezone-aware.")
    return max(0.0, (end - start).total_seconds())
