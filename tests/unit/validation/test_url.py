from django.core.exceptions import ValidationError
import pytest

from validation.url import validate_https_scheme


class TestValidateHTTPScheme:
    """Test the validate_https_scheme function."""

    error_message = "URL must use HTTPS."
    error_code = "invalid_scheme"

    @pytest.mark.parametrize(
        "url",
        (
            "",
            "example.com/path",
            "https://example.com",
            "HtTpS://example.com",
        ),
    )
    def test_validate_https_scheme_allows_valid_urls(self, url: str) -> None:
        """
        Given a URL that is empty, has no scheme or uses HTTPS
        When validate_https_scheme is called
        Then no ValidationError is raised
        """
        # Given
        valid_url = url

        # When
        result = validate_https_scheme(valid_url)

        # Then
        assert result is None

    @pytest.mark.parametrize(
        "url",
        (
            "http://example.com",
            "HTTP://example.com",
        ),
    )
    def test_validate_https_scheme_rejects_http_urls(self, url: str) -> None:
        """
        Given a URL that uses the HTTP scheme
        When validate_https_scheme is called
        Then a ValidationError is raised with the expected code and message
        """
        # Given
        invalid_url = url

        # When
        with pytest.raises(ValidationError) as exc_info:
            validate_https_scheme(invalid_url)

        # Then
        assert exc_info.value.code == self.error_code
        assert exc_info.value.message == self.error_message
