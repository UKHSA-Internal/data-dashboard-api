import os


def is_auth_enabled() -> bool:
    return str(os.environ.get("AUTH_ENABLED", "")).lower() in {
        "true",
        "1"
    }


def is_allow_missing_is_public_field() -> bool:
    return str(os.environ.get("ALLOW_MISSING_IS_PUBLIC_FIELD", "")).lower() in {
        "true",
        "1",
    }


AUTH_ENABLED = is_auth_enabled()
ALLOW_MISSING_IS_PUBLIC_FIELD = is_allow_missing_is_public_field()

ENFORCE_PUBLIC_DATA_ONLY = True
"""
If False, the non-authorized RBAC (Role-Based Access Control) paths will return public rows of 
          headline/time-series data and the authorized RBAC paths can include non-public rows 
          when permitted.

If True, this RBAC functionality will be suppressed and only public dashboard API data will be 
         returned. Exceptions are:
         a) The API endpoints /api/audit/* can still return public and non-public diagnostic data.
         b) Any API endpoints that serve metadata/master-table style data (not headline/time-series 
         row payloads) remain unfiltered too.
"""
