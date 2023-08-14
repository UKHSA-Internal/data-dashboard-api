import pytest
from rest_framework_api_key.permissions import HasAPIKey

from metrics.api.views.trends import TrendsViewBeta


class TestTrendsView:
    def test_sets_api_key_restriction(self):
        """
        Given an instance of the `TrendsView`
        When the `permission_classes` attribute is called
        Then the `HasAPIKey` class is in the returned list
        """
        # Given
        trends_view = TrendsViewBeta()

        # When
        permission_classes = trends_view.permission_classes

        # Then
        assert HasAPIKey in permission_classes

    def test_allowed_http_methods_contains_get_method(self):
        """
        Given an instance of the `TrendsView`
        When the `allowed_methods` attribute is called
        Then "GET" is in the returned list
        """
        # Given
        trends_view = TrendsViewBeta()

        # When
        allowed_methods: list[str] = trends_view.allowed_methods

        # Then
        assert "GET" in allowed_methods

    @pytest.mark.parametrize("excluded_http_method", ["POST", "PUT", "PATCH", "DELETE"])
    def test_allowed_http_methods_excludes_other_methods(
        self, excluded_http_method: str
    ):
        """
        Given an instance of the `TrendsView`
        When the `allowed_methods` attribute is called
        Then excluded HTTP methods are not in the returned list
        """
        # Given
        trends_view = TrendsViewBeta()

        # When
        allowed_methods: list[str] = trends_view.allowed_methods

        # Then
        assert excluded_http_method not in allowed_methods
