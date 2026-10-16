def choose_previous_version(model_versions, current_version):
    """Return the preceding item in an explicitly ordered version list."""
    versions = list(model_versions)
    if current_version not in versions:
        raise ValueError("current_version is not in model_versions.")
    index = versions.index(current_version)
    if index == 0:
        raise ValueError("No earlier version is available for rollback.")
    return versions[index - 1]
