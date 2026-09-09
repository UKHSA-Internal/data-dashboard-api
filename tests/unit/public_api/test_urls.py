import pytest
from unittest import mock

from public_api import construct_url_patterns_for_public_api
from public_api.metrics_interface.interface import MetricsPublicAPIInterface


class TestConstructUrlPatternsForPublicAPI:
    @pytest.mark.parametrize(
        ("prefix", "auth_enabled"),
        [
            pytest.param("api/example/prefix/", False, id="api/example/prefix/"),
            pytest.param("api/example/", False, id="api/example/"),
            pytest.param("api/public/", False, id="api/public/"),
            pytest.param("api/example/prefix/v2", False, id="api/example/prefix/v2"),
            pytest.param("api/example/v1", False, id="api/example/v1"),
            pytest.param("api/public/v2", False, id="api/public/v2"),
            pytest.param(
                "api/example/prefix/", True, id="api/example/prefix/-auth_enabled"
            ),
            pytest.param("api/example/", True, id="api/example/-auth_enabled"),
            pytest.param("api/public/", True, id="api/public/-auth_enabled"),
            pytest.param(
                "api/example/prefix/v2", True, id="api/example/prefix/v2-auth_enabled"
            ),
            pytest.param("api/example/v1", True, id="api/example/v1-auth_enabled"),
            pytest.param("api/public/v2", True, id="api/public/v2-auth_enabled"),
        ],
    )
    def test_sets_prefix_on_urls(self, prefix: str, auth_enabled: bool):
        """
        Given a prefix to prepend to the constructed urlpatterns
        When `construct_urlpatterns_for_public_api()` is called
        Then the prefix is added to the returned urlpatterns
        """
        # Given
        api_prefix = prefix

        # When
        with mock.patch.object(
            MetricsPublicAPIInterface,
            "is_auth_enabled",
            return_value=auth_enabled,
        ):
            urlpatterns = construct_url_patterns_for_public_api(prefix=api_prefix)

        if auth_enabled:
            urlpatterns = [
                urlpattern
                for urlpattern in urlpatterns
                if "robots.txt" not in urlpattern.pattern.describe()
            ]

        # Then
        assert all(
            prefix in urlpattern.pattern.regex.pattern for urlpattern in urlpatterns
        )
