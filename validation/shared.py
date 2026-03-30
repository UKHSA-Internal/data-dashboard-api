import typing as t
from django.conf import settings
from django.core.signing import loads, BadSignature, SignatureExpired
from django.utils import timezone

PAGE_PREVIEWS_TOKEN_SALT = getattr(settings, "PAGE_PREVIEWS_TOKEN_SALT", "preview-token")
CMS_AUTH_HEADER = "x-cms-auth"


def get_cms_auth_bearer_token(
    headers: t.Mapping[str, str],
) -> t.Optional[str]:
    """Extract Bearer token from the x-cms-auth header.

    Returns None if the header is missing or not in Bearer format.
    """
    auth_header = headers.get(CMS_AUTH_HEADER, "")
    if not auth_header or not auth_header.lower().startswith("bearer "):
        return None

    return auth_header.split(" ", 1)[1].strip()


def get_cms_auth_payload(token: str) -> t.Optional[dict]:
    """Decode CMS auth token payload.

    Returns None for invalid or malformed tokens.
    """
    try:
        payload = loads(token, salt=PAGE_PREVIEWS_TOKEN_SALT)
    except (BadSignature, SignatureExpired, ValueError, TypeError):
        return None

    if not isinstance(payload, dict):
        return None

    return payload


def validate_preview_hmac_token(token: str, *, page_id: t.Optional[int] = None) -> bool:
    """
    Validate and decode a CMS auth token. Optionally checks page_id.
    Returns True if valid, otherwise False.
    """
    payload = get_cms_auth_payload(token)
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
