import pytest
from unittest import mock

from public_api.version.v3.views.base import BaseNestedAPIViewV3


class TestNestedTimeSeriesView(BaseNestedAPIViewV3):
    """
    Minimal concrete implementation so BaseNestedAPITimeSeriesView can be instantiated
    during unit tests.
    """

    lookup_field = "mock"

    serializer_class = mock.MagicMock


@pytest.fixture
class TestPublicApi:

    # Timeseries gives timeseries data
    # Headline gives headline data
    # Test theme list
    # Test theme detail
    # Test subtheme list
    # Test subtheme detail
    # Test topic list
    # Test topic detail
    # Test geography type list
    # Test geography type detail
    # Test geography metric list
    # Test geography metric detail
