import re


def validate_version(version):
    if not isinstance(version, str) or not re.fullmatch(r"v[0-9]+\.[0-9]+\.[0-9]+", version):
        raise ValueError("Version must use semantic format such as v1.0.0.")
    return version


def compare_versions(first, second):
    a = tuple(map(int, validate_version(first)[1:].split(".")))
    b = tuple(map(int, validate_version(second)[1:].split(".")))
    return (a > b) - (a < b)


def next_patch(version):
    major, minor, patch = map(int, validate_version(version)[1:].split("."))
    return f"v{major}.{minor}.{patch + 1}"
