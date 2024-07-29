from unittest import mock

import pytest

from public_api.common.utils import return_request_serializer
from public_api.serializers.api_time_series_request_serializer import (
    APITimeSeriesRequestSerializer,
)
from public_api.v2.serializers.api_time_series_request_serializer import (
    APITimeSeriesRequestSerializerV2,
)


class TestReturnRequestSerializer:
    def test_return_request_serializer_returns_version_one(self):
        """
        Given a request version of v1
        When `return_request_serializer` is called
        Then an instance of `APITimeseriesRequestSerializer` is
            returned.
        """
        # Given
        mocked_request = mock.MagicMock()
        mocked_request["request"].version = "v1"

        # When
        timeseries_serializer = return_request_serializer(
            serializer_context=mocked_request,
        )

        # Then
        assert type(timeseries_serializer) == APITimeSeriesRequestSerializer

    def test_return_request_serializer_returns_version_two(self):
        """
        Given a request version of v2
        When `return_request_serializer` is called
        Then an instance of `APITimeseriesRequestSerializerv2` is
            returned.
        """
        # Given
        mocked_request = mock.MagicMock()
        mocked_request["request"].version = "v2"

        # When
        timeseries_serializer = return_request_serializer(
            serializer_context=mocked_request,
        )

        # Then
        assert type(timeseries_serializer) == APITimeSeriesRequestSerializerV2
