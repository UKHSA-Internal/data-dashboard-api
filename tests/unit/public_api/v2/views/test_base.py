import pytest
from unittest import mock

from public_api.version_02.views.base import BaseNestedAPITimeSeriesViewV2


class TestNestedTimeSeriesView(BaseNestedAPITimeSeriesViewV2):
    """
    Minimal concrete implementation so BaseNestedAPITimeSeriesView can be instantiated
    during unit tests.
    """

    lookup_field = "mock"

    serializer_class = mock.MagicMock


class TestBaseNestedAPITimeSeriesViewV2:
    def test_raises_error_for_lookup_field_property(self):
        """
        Given an instance of the `BaseNestedAPITimeSeriesView`
        When the `lookup_field` property is called
        Then a `NotImplementedError` is raised
            as this should be implemented by the child class
        """
        # Given
        base_view = BaseNestedAPITimeSeriesViewV2()

        # When / Then
        with pytest.raises(NotImplementedError):
            base_view.lookup_field

    def test_raises_error_for_serializer_class_property(self):
        """
        Given an instance of the `BaseNestedAPITimeSeriesView`
        When the `serializer_class` property is called
        Then a `NotImplementedError` is raised
            as this should be implemented by the child class
        """
        # Given
        base_view = BaseNestedAPITimeSeriesViewV2()

        # When / Then
        with pytest.raises(NotImplementedError):
            base_view.serializer_class


class TestGetAddsPrivateHeaderForNonPublicRequests:
    """
    Tests for the newly added private Cache-Control header behaviour in the `get()` method.
    """

    @mock.patch(
        "public_api.version_02.views.base.backend.JSONWebTokenAuthentication.authenticate"
    )
    @mock.patch("public_api.version_02.views.base.Response")
    @mock.patch("public_api.version_02.views.base.APITimeSeriesRequestSerializerv2")
    def test_private_header_added_when_valid_jwt(
        self,
        mock_request_serializer_class: mock.MagicMock,
        mock_response_class: mock.MagicMock,
        mock_backend_auth_authenticate: mock.MagicMock,
    ):
        """
        Given `backend.JSONWebTokenAuthentication.authenticate()` returns True
        When `get()` is called
        Then the response contains Cache-Control: private, no-cache
        """
        # Given
        mock_backend_auth_authenticate.return_value = True

        mocked_request = mock.MagicMock()

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
        response = base_view.get(mocked_request)

        # Then
        mock_backend_auth_authenticate.assert_called_once_with(mocked_request)
        mocked_response.__setitem__.assert_called_once_with(
            "Cache-Control", "private, no-cache"
        )
        assert response == mocked_response

    @mock.patch(
        "public_api.version_02.views.base.backend.JSONWebTokenAuthentication.authenticate"
    )
    @mock.patch("public_api.version_02.views.base.Response")
    @mock.patch("public_api.version_02.views.base.APITimeSeriesRequestSerializerv2")
    def test_private_header_not_added_when_is_valid_non_public_request_is_false(
        self,
        mock_request_serializer_class: mock.MagicMock,
        mock_response_class: mock.MagicMock,
        mock_backend_auth_authenticate: mock.MagicMock,
    ):
        """
        Given `_is_valid_non_public_request()` returns False
        When `get()` is called
        Then the response does NOT contain a private Cache-Control header
        """
        # Given
        mock_backend_auth_authenticate.return_value = False

        mocked_request = mock.MagicMock()

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
        response = base_view.get(mocked_request)

        # Then
        mock_backend_auth_authenticate.assert_called_once_with(mocked_request)
        mocked_response.__setitem__.assert_not_called()
        assert response == mocked_response
