import config
from metrics.api import urls
from metrics.api.urls_construction import construct_urlpatterns


class TestUrls:
    def test_construct_urlpatterns_is_called_to_provide_urls(self):
        """
        Given the `urlpatterns` from the `urls` file
        When this is ingested by the application
        Then the urlpatterns returned from `construct_urlpatterns()`
            are included
        """
        # Given / When
        urlpatterns = urls.urlpatterns
        url_regex_patterns = [
            urlpattern.pattern.regex.pattern for urlpattern in urlpatterns
        ]

        # Then
        constructed_urlpatterns = construct_urlpatterns(app_mode=config.APP_MODE)

        for constructed_urlpattern in constructed_urlpatterns:
            pattern = constructed_urlpattern.pattern.regex.pattern
            assert pattern in url_regex_patterns
