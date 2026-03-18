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

# If False, non-authorized RBAC paths return only public headline/time-series rows,
#           while authorized RBAC paths can include non-public rows when permitted.
# If True, RBAC non-public row access is suppressed and only public dashboard API
#          row data is returned, except:
#          a) `/api/audit/*` endpoints can still return public and non-public
#              diagnostics.
#          b) Metadata/master-table endpoints (not headline/time-series rows)
#             remain unfiltered.
ENFORCE_PUBLIC_DATA_ONLY = True
