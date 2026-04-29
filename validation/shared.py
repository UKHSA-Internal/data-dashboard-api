import logging
import typing as t

from django.conf import settings
from django.core.signing import BadSignature, SignatureExpired, loads
from django.utils import timezone

logger = logging.getLogger(__name__)

CMS_AUTH_HEADER = "x-cms-auth"
CACHE_CONTROL_HEADER = "Cache-Control"
# we support only one level of disablement and no-store is the most resolute
CACHE_CONTROL_CACHE_DISABLED = "no-store"  # must match exactly


def get_cms_auth_bearer_token(
    headers: t.Mapping[str, str],
) -> str | None:
    """Extract Bearer token from the x-cms-auth header.

    Returns None if the header is missing or not in Bearer format.
    """
    auth_header = headers.get(CMS_AUTH_HEADER, "")
    if not auth_header or not auth_header.lower().startswith("bearer "):
        return None

    return auth_header.split(" ", 1)[1].strip()


def get_cms_auth_payload(token: str) -> dict | None:
    """Decode CMS auth token payload.

    Returns None for invalid or malformed tokens.
    """
    try:
        payload = loads(token, salt=settings.PAGE_PREVIEWS_TOKEN_SALT)
    except (BadSignature, SignatureExpired, ValueError, TypeError):
        return None

    if not isinstance(payload, dict):
        return None

    return payload


def validate_preview_hmac_payload(
    payload: dict | None, *, page_id: int | None = None
) -> bool:
    """Validate decoded CMS auth payload fields.

    Expects a decoded payload dict and checks required claims.
    """
    if payload is None:
        return False

    exp = payload.get("exp")
    if exp is None or timezone.now().timestamp() > exp:
        return False

    if page_id is not None:
        payload_page_id = payload.get("page_id")
        if payload_page_id is None or int(payload_page_id) != int(page_id):
            return False

    return True


def validate_preview_hmac_token(
    token: str,
    *,
    page_id: int | None = None,
    include_payload: bool = False,
) -> bool | dict:
    """
    Validate and decode a CMS auth token. Optionally checks page_id.

    Returns:
        - bool by default
        - decoded payload dict when include_payload=True and token is valid
    """
    payload = get_cms_auth_payload(token)
    is_valid = validate_preview_hmac_payload(payload, page_id=page_id)
    if not is_valid:
        return False

    if include_payload:
        return payload or {}

    return True


def format_child_and_parent_theme_name(name: str) -> str:
    """Naming of themes can sometimes use a `-` rather than `_` in their naming
        This formats these strings to ensure `-` is replaced with `_` for
        selecting enums.

    Args:
        name: string containing either `parent_theme` or `child_theme`

    Returns:
        name: string with formatted `parent_theme` or `child_theme` name

    """
    return name.replace("-", "_").upper()


def get_cache_control_header(
    headers: t.Mapping[str, str],
) -> str | None:
    """Extract Cache-Control value from the header.
    Returns None if the header is missing.
    All elements in CACHE_CONTROL_HEADER must be matched
             in request header
    Example: CACHE_CONTROL_HEADER = 'private, no-cache'
             cache_control_header = 'no-cache, private'
             This will return True

    """
    cache_control_header = headers.get(CACHE_CONTROL_HEADER, "")

    required = {p.strip() for p in CACHE_CONTROL_CACHE_DISABLED.split(",")}
    actual = {p.strip() for p in cache_control_header.split(",")}

    if not required.issubset(actual):
        return None

    return cache_control_header
