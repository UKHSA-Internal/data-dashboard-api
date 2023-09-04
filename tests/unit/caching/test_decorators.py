from unittest import mock

from caching.decorators import retrieve_response_from_cache_or_calculate
from caching.management import CacheManagement, CacheMissError

MODULE_PATH = "caching.decorators"


class TestRetrieveResponseFromCacheOrCalculate:
    def test_retrieve_response_from_cache_or_calculate_can_return_response_if_available(
        self,
    ):
        """
        Given a mocked request and a `CacheManagement` object
            which returns the expected response
        When `retrieve_response_from_cache_or_calculate()` is called
        Then the expected response is returned
        """
        # Given
        mocked_request = mock.MagicMock(method="POST")
        mocked_expected_response = mock.Mock()
        mocked_cache_management = mock.Mock()
        mocked_cache_management.retrieve_item_from_cache.return_value = (
            mocked_expected_response
        )

        # When
        retrieved_response = retrieve_response_from_cache_or_calculate(
            mock.Mock(),  # view_function
            mock.Mock(),
            mocked_request,
            cache_management=mocked_cache_management,
        )

        # Then
        assert retrieved_response == mocked_expected_response

    @mock.patch(f"{MODULE_PATH}._calculate_response_from_view")
    def test_retrieve_response_from_cache_or_calculate_does_not_recalculate_response_if_already_available(
        self, spy_calculate_response_from_view: mock.MagicMock
    ):
        """
        Given a mocked request and a `CacheManagement` object
            which returns the expected response
        When `retrieve_response_from_cache_or_calculate()` is called
        Then `_calculate_response_from_view()` is not called

        Patches:
            `spy_calculate_response_from_view`: For the main assertion
        """
        # Given
        mocked_request = mock.MagicMock(method="POST")
        mocked_expected_response = mock.Mock()
        mocked_cache_management = mock.Mock()
        mocked_cache_management.retrieve_item_from_cache.return_value = (
            mocked_expected_response
        )

        # When
        retrieve_response_from_cache_or_calculate(
            mock.Mock(),  # view_function
            mock.Mock(),
            mocked_request,
            cache_management=mocked_cache_management,
        )

        # Then
        spy_calculate_response_from_view.assert_not_called()

    @mock.patch.object(CacheManagement, "build_cache_entry_key_for_request")
    @mock.patch(f"{MODULE_PATH}._calculate_response_from_view")
    def test_retrieve_response_from_cache_or_calculate_recalculate_response_when_not_available(
        self,
        spy_calculate_response_from_view: mock.MagicMock,
        spy_build_cache_entry_key_for_request: mock.MagicMock,
    ):
        """
        Given a mocked request which will miss the cache
        When `retrieve_response_from_cache_or_calculate()` is called
        Then `_calculate_response_from_view()` is called with the correct args

        Patches:
            `spy_calculate_response_from_view`: For the main assertion
            `spy_build_cache_entry_key_for_request`: To isolate the side effect
                of having to build a hash from mocked input data
        """
        # Given
        mocked_request = mock.MagicMock(method="POST")
        mocked_view_function = mock.Mock()
        mocked_args = [mock.Mock(), mocked_request, mock.Mock()]
        mocked_kwargs = {"key_a": mock.Mock(), "key_b": mock.Mock()}

        # When
        retrieved_response = retrieve_response_from_cache_or_calculate(
            mocked_view_function, *mocked_args, **mocked_kwargs  # view_function
        )

        # Then
        spy_calculate_response_from_view.assert_called_with(
            mocked_view_function, *mocked_args, **mocked_kwargs
        )

        assert retrieved_response == spy_calculate_response_from_view.return_value

    @mock.patch(f"{MODULE_PATH}._calculate_response_from_view")
    def test_retrieve_response_from_cache_or_calculate_calls_save_item_in_cache_when_recalculating_response(
        self, spy_calculate_response_from_view: mock.MagicMock
    ):
        """
        Given a mocked request which will miss the cache
        When `retrieve_response_from_cache_or_calculate()` is called
        Then `save_item_in_cache()` is called from the `CacheManagement` object

        Patches:
            `spy_calculate_response_from_view`: To isolate the return value
                which is then passed to the main assertion
        """
        # Given
        mocked_view_function = mock.Mock()
        mocked_args = [mock.Mock(), mock.MagicMock(method="POST"), mock.Mock()]
        spy_cache_management = mock.Mock()
        spy_cache_management.retrieve_item_from_cache.side_effect = CacheMissError()
        mocked_kwargs = {
            "key_a": mock.Mock(),
            "key_b": mock.Mock(),
            "cache_management": spy_cache_management,
        }

        # When
        retrieve_response_from_cache_or_calculate(
            mocked_view_function, *mocked_args, **mocked_kwargs  # view_function
        )

        # Then
        spy_cache_management.save_item_in_cache.assert_called_once_with(
            cache_entry_key=spy_cache_management.build_cache_entry_key_for_request.return_value,
            item=spy_calculate_response_from_view.return_value,
        )
