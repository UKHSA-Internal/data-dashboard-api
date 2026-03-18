from django.core.exceptions import ValidationError


def validate_https_scheme(value: str) -> None:
    """Raise if URL has a scheme that is not https."""
    if not value or "://" not in value:
        return

    scheme = value.split("://", 1)[0].lower()
    if scheme != "https":
        error_message = "URL must use HTTPS."
        raise ValidationError(
            error_message,
            code="invalid_scheme",
            params={"value": value},
        )
