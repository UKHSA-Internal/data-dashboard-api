import typing as t
from django.conf import settings
from django.core.signing import loads, BadSignature, SignatureExpired
from django.utils import timezone

PAGE_PREVIEWS_TOKEN_SALT = getattr(settings, "PAGE_PREVIEWS_TOKEN_SALT", "preview-token")

def validate_preview_hmac_token(token: str, *, page_id: t.Optional[int] = None) -> dict:
    """
    Validate and decode a preview HMAC token. Optionally checks page_id.
    Returns the decoded payload if valid, raises ValueError if invalid.
    """
    try:
        payload = loads(token, salt=PAGE_PREVIEWS_TOKEN_SALT)
    except (BadSignature, SignatureExpired, ValueError, TypeError):
        raise ValueError("Invalid or expired token")

    exp = payload.get("exp")
    if exp is None or timezone.now().timestamp() > exp:
        raise ValueError("Token expired")

    if page_id is not None:
        payload_page_id = payload.get("page_id")
        if payload_page_id is None or int(payload_page_id) != int(page_id):
            raise ValueError("Token page_id mismatch")

    return payload

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
