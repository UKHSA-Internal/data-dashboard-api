import pytest
from unittest import mock

from public_api.views.base import BaseNestedAPITimeSeriesView


class TestNestedTimeSeriesView(BaseNestedAPITimeSeriesView):
    """
    Minimal concrete implementation so BaseNestedAPITimeSeriesView can be instantiated
    during unit tests.
    """

    lookup_field = "mock"

    serializer_class = mock.MagicMock


class TestBaseNestedAPITimeSeriesView:
    def test_raises_error_for_lookup_field_property(self):
        """
        Given an base_view of the `BaseNestedAPITimeSeriesView`
        When the `lookup_field` property is called
        Then a `NotImplementedError` is raised
            as this should be implemented by the child class
        """
        # Given
        base_view = BaseNestedAPITimeSeriesView()

        # When / Then
        with pytest.raises(NotImplementedError):
            base_view.lookup_field

    def test_raises_error_for_serializer_class_property(self):
        """
        Given an base_view of the `BaseNestedAPITimeSeriesView`
        When the `serializer_class` property is called
        Then a `NotImplementedError` is raised
            as this should be implemented by the child class
        """
        # Given
        base_view = BaseNestedAPITimeSeriesView()

        # When / Then
        with pytest.raises(NotImplementedError):
            base_view.serializer_class


class TestIsValidNonPublicRequest:
    """
    Tests for the `_is_valid_non_public_request()` static method.
    """

    def test_returns_true_when_is_public_false_and_authenticated(self):
        mocked_request = mock.MagicMock()
        mocked_request.query_params = {"is-public": "false"}
        mocked_request.auth = mock.MagicMock(return_value=True)
        base_view = BaseNestedAPITimeSeriesView()

        result = base_view._is_valid_non_public_request(mocked_request)

        assert result is True

    def test_returns_false_when_is_public_false_but_not_authenticated(self):
        mocked_request = mock.MagicMock()
        mocked_request.query_params = {"is-public": "false"}
        mocked_request.auth = mock.MagicMock(side_effect=TypeError)
        base_view = BaseNestedAPITimeSeriesView()

        result = base_view._is_valid_non_public_request(mocked_request)

        assert result is False

    def test_returns_false_when_is_public_true_even_if_authenticated(self):
        mocked_request = mock.MagicMock()
        mocked_request.query_params = {"is-public": "true"}
        mocked_request.auth = mock.MagicMock(return_value=True)
        base_view = BaseNestedAPITimeSeriesView()

        result = base_view._is_valid_non_public_request(mocked_request)

        assert result is False

    def test_returns_false_when_is_public_missing(self):
        mocked_request = mock.MagicMock()
        mocked_request.query_params = {}
        mocked_request.auth = mock.MagicMock(return_value=True)
        base_view = BaseNestedAPITimeSeriesView()

        result = base_view._is_valid_non_public_request(mocked_request)

        assert result is False

    def test_returns_false_when_auth_returns_false(self):
        mocked_request = mock.MagicMock()
        mocked_request.query_params = {"is-public": "false"}
        mocked_request.auth = mock.MagicMock(return_value=False)
        base_view = BaseNestedAPITimeSeriesView()

        result = base_view._is_valid_non_public_request(mocked_request)

        assert result is False
        
        

class TestGetAddsPrivateHeaderForNonPublicRequests:
    """
    Tests for the newly added private Cache-Control header behaviour in the `get()` method.
    """

    @mock.patch("public_api.views.base.BaseNestedAPITimeSeriesView._is_valid_non_public_request")
    @mock.patch("public_api.views.base.Response")
    @mock.patch("public_api.views.base.APITimeSeriesRequestSerializer")
    def test_private_header_added_when_is_valid_non_public_request_is_true(
        self,
        mock_request_serializer_class: mock.MagicMock,
        mock_response_class: mock.MagicMock,
        spy_is_valid_non_public_request: mock.MagicMock,
    ):
        """
        Given `_is_valid_non_public_request()` returns True
        When `get()` is called
        Then the response contains Cache-Control: private, no-cache
        """
        # Given
        spy_is_valid_non_public_request.return_value = True

        mocked_request = mock.MagicMock()
        mocked_request.query_params = {}

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
        spy_is_valid_non_public_request.assert_called_once_with(request=mocked_request)
        mocked_response.__setitem__.assert_called_once_with(
            "Cache-Control", "private, no-cache"
        )
        assert response == mocked_response

    @mock.patch("public_api.views.base.BaseNestedAPITimeSeriesView._is_valid_non_public_request")
    @mock.patch("public_api.views.base.Response")
    @mock.patch("public_api.views.base.APITimeSeriesRequestSerializer")
    def test_private_header_not_added_when_is_valid_non_public_request_is_false(
        self,
        mock_request_serializer_class: mock.MagicMock,
        mock_response_class: mock.MagicMock,
        spy_is_valid_non_public_request: mock.MagicMock,
    ):
        """
        Given `_is_valid_non_public_request()` returns False
        When `get()` is called
        Then the response does NOT contain a private Cache-Control header
        """
        # Given
        spy_is_valid_non_public_request.return_value = False

        mocked_request = mock.MagicMock()
        mocked_request.query_params = {}

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
        spy_is_valid_non_public_request.assert_called_once_with(request=mocked_request)
        mocked_response.__setitem__.assert_not_called()
        assert response == mocked_response

