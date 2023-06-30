from unittest import mock

import pytest
from rest_framework.serializers import ValidationError
from wagtail.api.v2.views import PageSerializer
from wagtail.models import Page

from cms.dashboard.serializers import CMSDraftPagesSerializer


class TestCMSDraftPagesSerializer:
    def test_to_representation_raises_error_if_page_has_no_unpublished_changes(self):
        """
        Given a mocked `Page` which has no unpublished changes
        When `to_representation()` is called
            from an instance of the `CMSDraftPagesSerializer`
        Then a `ValidationError` is raised
        """
        # Given
        mocked_page = mock.Mock(spec_set=Page, has_unpublished_changes=False)
        serializer = CMSDraftPagesSerializer(instance=mocked_page)

        # When / Then
        with pytest.raises(ValidationError):
            serializer.to_representation(instance=mocked_page)

    @mock.patch.object(PageSerializer, "to_representation")
    def test_to_representation_calls_super_when_page_has_unpublished_changes(
        self, spy_to_representation: mock.MagicMock
    ):
        """
        Given a mocked `Page` which has unpublished changes
        When `to_representation()` is called
            from an instance of the `CMSDraftPagesSerializer`
        Then the `super().to_representation()` method is called

        Patches:
            `spy_to_representation`: For the main assertion

        """
        # Given
        mocked_page = mock.Mock(spec_set=Page, has_unpublished_changes=True)
        serializer = CMSDraftPagesSerializer(instance=mocked_page)

        # When
        representation = serializer.to_representation(instance=mocked_page)

        # Then
        assert representation == spy_to_representation.return_value
        spy_to_representation.assert_called_once_with(instance=mocked_page)
