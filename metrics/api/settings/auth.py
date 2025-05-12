import os


def is_auth_enabled() -> bool:
    return str(os.environ.get("AUTH_ENABLED", "")).lower() in {"true", "1"}


AUTH_ENABLED = is_auth_enabled()
