import pytest

from public_api import construct_urlpatterns_for_public_api


class TestConstructUrlPatternsForPublicAPI:
    @pytest.mark.parametrize(
        "prefix", ["api/example/prefix/", "api/example/", "api/public/"]
    )
    def test_sets_prefix_on_urls(self, prefix: str):
        """
        Given a prefix to prepend to the constructed urlpatterns
        When `construct_urlpatterns_for_public_api()` is called
        Then the prefix is added to the returned urlpatterns
        """
        # Given
        api_prefix = prefix

        # When
        urlpatterns = construct_urlpatterns_for_public_api(prefix=api_prefix)

        # Then
        assert all(
            prefix in urlpattern.pattern.regex.pattern for urlpattern in urlpatterns
        )
