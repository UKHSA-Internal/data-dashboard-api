from unittest import mock

import pytest

from metrics.api.views.downloads import DownloadsView


class TestDownloadsView:
    def test_get_serializer_raises_error(self):
        """
        Given an invalid `metric_group`
        When the `_get_serializer_class()` method is called.
        Then a `ValueError` is raised
        """
        # Given
        downloads_view = DownloadsView()
        invalid_metric_group = "invalid_metric_group"

        # When / Then
        with pytest.raises(ValueError):
            downloads_view._get_serializer_class(
                queryset=mock.MagicMock(),
                metric_group=invalid_metric_group,
            )
