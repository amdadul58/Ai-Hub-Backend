ROLE_PERMISSIONS = {
    "admin": {"read", "write", "delete", "manage_users", "manage_models"},
    "user": {"read", "write"},
    "viewer": {"read"},
}


def has_permission(role, permission):
    return permission in ROLE_PERMISSIONS.get(role, set())


def require_permission(role, permission):
    if not has_permission(role, permission):
        raise PermissionError(f"Role {role!r} lacks permission {permission!r}.")
    return True
