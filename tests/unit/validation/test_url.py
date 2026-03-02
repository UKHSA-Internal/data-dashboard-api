from validation.url import validate_https_scheme
import pytest
from django.core.exceptions import ValidationError


class TestValidateHTTPScheme:
    """Test the validate_https_scheme function."""

    error_message = "URL must use HTTPS."
    error_code = "invalid_scheme"

    def test_validate_https_scheme_empty_string(self):
        """Should not raise for empty string."""
        assert validate_https_scheme("") is None

    def test_validate_https_scheme_no_scheme(self):
        """Should not raise for URL without scheme."""
        assert validate_https_scheme("example.com/path") is None

    def test_validate_https_scheme_http_scheme(self):
        """Should raise for http scheme."""
        with pytest.raises(ValidationError) as exc_info:
            validate_https_scheme("http://example.com")
        assert exc_info.value.code == self.error_code
        assert self.error_message in str(exc_info.value)

    def test_validate_https_scheme_https_scheme(self):
        """Should not raise for https scheme."""
        assert validate_https_scheme("https://example.com") is None

    def test_validate_https_scheme_mixed_case_http(self):
        """Should raise for mixed case http scheme."""
        with pytest.raises(ValidationError) as exc_info:
            validate_https_scheme("HTTP://example.com")
        assert exc_info.value.code == self.error_code
        assert self.error_message in str(exc_info.value)

    def test_validate_https_scheme_mixed_case_https(self):
        """Should not raise for mixed case https scheme."""
        validate_https_scheme("HtTpS://example.com")
