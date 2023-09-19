from django.urls import URLPattern

from ingestion.api.urls import construct_urlpatterns_for_ingestion


class TestConstructUrlPatternsForIngestion:
    def test_returns_correct_url_patterns(self):
        """
        Given a url prefix
        When `construct_urlpatterns_for_ingestion()` is called
        Then the list of the 1 expected url pattern is returned
        """
        # Given
        prefix = "fake-api/"

        # When
        constructed_urlpatterns: list[URLPattern] = construct_urlpatterns_for_ingestion(
            prefix=prefix
        )

        # Then
        assert len(constructed_urlpatterns) == 1
        assert (
            constructed_urlpatterns[0].pattern.regex.pattern == f"^{prefix}ingestion/v1"
        )
