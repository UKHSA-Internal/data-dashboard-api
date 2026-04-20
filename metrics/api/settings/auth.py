import os


def is_auth_enabled() -> bool:
    return str(os.environ.get("AUTH_ENABLED", "")).lower() in {"true", "1"}


def is_allow_missing_is_public_field() -> bool:
    return str(os.environ.get("ALLOW_MISSING_IS_PUBLIC_FIELD", "")).lower() in {
        "true",
        "1",
    }


AUTH_ENABLED = is_auth_enabled()
ALLOW_MISSING_IS_PUBLIC_FIELD = is_allow_missing_is_public_field()
