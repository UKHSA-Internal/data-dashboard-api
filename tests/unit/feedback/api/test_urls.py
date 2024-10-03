from django.urls import URLPattern

from feedback.api.urls import construct_urlpatterns_for_feedback


class TestConstructUrlPatternsForFeedback:
    def test_returns_correct_url_patterns(self):
        """
        Given a url prefix
        When `construct_urlpatterns_for_feedback()` is called
        Then the list of the 1 expected url pattern is returned
        """
        # Given
        prefix = "fake-api/"

        # When
        constructed_urlpatterns: list[URLPattern] = construct_urlpatterns_for_feedback(
            prefix=prefix
        )

        # Then
        assert len(constructed_urlpatterns) == 2
        assert (
            constructed_urlpatterns[0].pattern.regex.pattern
            == f"^{prefix}suggestions/v1"
        )
        assert (
            constructed_urlpatterns[1].pattern.regex.pattern
            == f"^{prefix}suggestions/v2"
        )
