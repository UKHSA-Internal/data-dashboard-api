class UserPermissionsFactory(dict):
    def __init__(self, permissions, has_global_access=False):
        self["permission_sets"] = permissions
        self["summary"] = {
            "has_global_access": has_global_access,
            "total_permission_sets": len(permissions),
        }
