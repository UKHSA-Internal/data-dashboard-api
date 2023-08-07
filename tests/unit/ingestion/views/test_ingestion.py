import pytest
from rest_framework.parsers import MultiPartParser
from rest_framework_api_key.permissions import HasAPIKey

from ingestion.api.views.ingestion import IngestionView


class TestIngestionView:
    def test_sets_api_key_restriction(self):
        """
        Given an instance of the `IngestionView`
        When the `permission_classes` attribute is called
        Then the `HasAPIKey` class is in the returned list
        """
        # Given
        ingestion_view = IngestionView()

        # When
        permission_classes = ingestion_view.permission_classes

        # Then
        assert HasAPIKey in permission_classes

    def test_sets_multi_part_parser(self):
        """
        Given an instance of the `IngestionView`
        When the `parser_classes` attribute is called
        Then the `MultiPartParser` class is in the returned list
        """
        # Given
        ingestion_view = IngestionView()

        # When
        parser_classes = ingestion_view.parser_classes

        # Then
        assert MultiPartParser in parser_classes

    def test_allowed_http_methods_contains_post_method(self):
        """
        Given an instance of the `IngestionView`
        When the `allowed_methods` attribute is called
        Then "POST" is in the returned list
        """
        # Given
        ingestion_view = IngestionView()

        # When
        allowed_methods = ingestion_view.allowed_methods

        # Then
        assert "POST" in allowed_methods

    @pytest.mark.parametrize("excluded_http_method", ["GET", "PUT", "PATCH", "DELETE"])
    def test_allowed_http_methods_exclues_other_methods(
        self, excluded_http_method: str
    ):
        """
        Given an instance of the `IngestionView`
        When the `allowed_methods` attribute is called
        Then excluded HTTP methods are not in the returned list
        """
        # Given
        ingestion_view = IngestionView()

        # When
        allowed_methods = ingestion_view.allowed_methods

        # Then
        assert excluded_http_method not in allowed_methods
