import pytest
from unittest import mock

from django.core.exceptions import ImproperlyConfigured

from metrics.data.models.api_models import APITimeSeries, APIHeadline
from public_api.version.v3.serializers.api_request_serializer import (
    APIRequestSerializerv3,
)
from public_api.version.v3.views.base import BaseNestedAPIViewV3


class TestNestedTimeSeriesView(BaseNestedAPIViewV3):
    """
    Minimal concrete implementation so BaseNestedAPITimeSeriesView can be instantiated
    during unit tests.
    """

    lookup_field = "mock"

    serializer_class = mock.MagicMock


class TestBaseNestedAPIViewV3:
    def test_raises_error_for_lookup_field_property(self):
        """
        Given an instance of the `BaseNestedAPITimeSeriesView`
        When the `lookup_field` property is called
        Then a `NotImplementedError` is raised
            as this should be implemented by the child class
        """
        # Given
        base_view = BaseNestedAPIViewV3()

        # When / Then
        with pytest.raises(NotImplementedError):
            _ = base_view.lookup_field

    def test_raises_error_for_serializer_class_property(self):
        """
        Given an instance of the `BaseNestedAPITimeSeriesView`
        When the `serializer_class` property is called
        Then a `NotImplementedError` is raised
            as this should be implemented by the child class
        """
        # Given
        base_view = BaseNestedAPIViewV3()

        # When / Then
        with pytest.raises(NotImplementedError):
            _ = base_view.serializer_class

    @pytest.mark.parametrize(
        "model, serializer",
        [
            (APIHeadline, APIRequestSerializerv3),
            (APITimeSeries, APIRequestSerializerv3),
        ],
    )
    def test_resolves_the_correct_api_model(
        self,
        model,
        serializer,
    ):
        """f
        Given an instance of the `BaseNestedAPIViewV3`
        When the `api_model` property is set and `get_queryset()` is called
        Then the expected API model's queryset is returned.
        """
        base_view = BaseNestedAPIViewV3()
        base_view.api_model = model

        assert base_view.get_queryset().model is model

    def test_raises_error_for_get_queryset_not_implemented(self):
        """
        Given an instance of the `BaseNestedAPITimeSeriesView`
        When the `get_queryset` method is called and the `api_model` property has not been set
        Then a `ImproperlyConfigured` exception is raised.
        """
        # Given
        base_view = BaseNestedAPIViewV3()
        base_view.api_model = None

        # Mock the final serializer
        mock_data_serializer = mock.MagicMock()
        mock_data_serializer.data = {"foo": "bar"}

        base_view.get_serializer = mock.MagicMock(return_value=mock_data_serializer)

        with pytest.raises(ImproperlyConfigured):
            base_view.get_queryset()


class TestGetAddsPrivateHeaderForNonPublicRequests:
    """
    Tests for the newly added private Cache-Control header behaviour in the `get()` method.
    """

    @mock.patch("public_api.version.v3.views.base.Response")
    @mock.patch("public_api.version.v3.views.base.APIRequestSerializerv3")
    def test_private_header_added_when_valid_jwt(
        self,
        mock_request_serializer_class: mock.MagicMock,
        mock_response_class: mock.MagicMock,
    ):
        """
        Given `backend.JSONWebTokenAuthentication.authenticate()` returns True
        When `get()` is called
        Then the response contains Cache-Control: private, no-cache
        """
        # Given
        mocked_request = mock.MagicMock(auth="valid_jwt")

        mocked_slice = [mock.MagicMock()]
        mock_request_serializer = mock.MagicMock()
        mock_request_serializer.build_timeseries_dto_slice.return_value = mocked_slice
        mock_request_serializer_class.return_value = mock_request_serializer

        mock_data_serializer = mock.MagicMock()
        mock_data_serializer.data = {"foo": "bar"}

        base_view = TestNestedTimeSeriesView()
        base_view.get_serializer = mock.MagicMock(return_value=mock_data_serializer)

        mocked_response = mock.MagicMock()
        mock_response_class.return_value = mocked_response

        # When
        with mock.patch(
            "public_api.auth.MetricsPublicAPIInterface.is_auth_enabled",
            return_value=True,
        ):
            response = base_view.get(mocked_request)

        # Then
        mocked_response.__setitem__.assert_called_once_with(
            "Cache-Control", "private, no-cache"
        )
        assert response == mocked_response

    @mock.patch("public_api.version.v3.views.base.Response")
    @mock.patch("public_api.version.v3.views.base.APIRequestSerializerv3")
    def test_private_header_not_added_when_is_valid_non_public_request_is_false(
        self,
        mock_request_serializer_class: mock.MagicMock,
        mock_response_class: mock.MagicMock,
    ):
        """
        Given `_is_valid_non_public_request()` returns False
        When `get()` is called
        Then the response does NOT contain a private Cache-Control header
        """
        # Given

        mocked_request = mock.MagicMock()
        mocked_request.auth = None

        # Mock DTO slice creation
        mocked_slice = [mock.MagicMock()]
        mock_request_serializer = mock.MagicMock()
        mock_request_serializer.build_timeseries_dto_slice.return_value = mocked_slice
        mock_request_serializer_class.return_value = mock_request_serializer

        # Mock the final serializer
        mock_data_serializer = mock.MagicMock()
        mock_data_serializer.data = {"foo": "bar"}

        base_view = TestNestedTimeSeriesView()
        base_view.get_serializer = mock.MagicMock(return_value=mock_data_serializer)

        # Mock Response
        mocked_response = mock.MagicMock()
        mock_response_class.return_value = mocked_response

        # When
        with mock.patch(
            "public_api.auth.MetricsPublicAPIInterface.is_auth_enabled",
            return_value=True,
        ):
            response = base_view.get(mocked_request)

        # Then
        mocked_response.__setitem__.assert_not_called()
        assert response == mocked_response
