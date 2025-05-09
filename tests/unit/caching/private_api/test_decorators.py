from unittest import mock

import pytest

from caching.internal_api_client import (
    CACHE_CHECK_HEADER_KEY,
    CACHE_FORCE_REFRESH_HEADER_KEY,
)
from caching.private_api.decorators import (
    CacheCheckResultedInMissError,
    _calculate_response_and_save_in_cache,
    _retrieve_response_from_cache_or_calculate,
)
from caching.private_api.management import CacheMissError

MODULE_PATH = "caching.private_api.decorators"


class TestRetrieveResponseFromCacheOrCalculate:
    # Tests for cache hits + no force refreshing
    def test_can_return_response_if_already_available(self):
        """
        Given a mocked request and a `CacheManagement` object
            which returns the expected response
        When `_retrieve_response_from_cache_or_calculate()` is called
        Then the expected response is returned
        """
        # Given
        mocked_request = mock.MagicMock(
            method="POST", headers={CACHE_FORCE_REFRESH_HEADER_KEY: False}
        )
        mocked_cache_management = mock.Mock()

        # When
        retrieved_response = _retrieve_response_from_cache_or_calculate(
            mock.Mock(),  # view_function
            None,  # timeout
            mock.Mock(),
            mocked_request,
            cache_management=mocked_cache_management,
        )

        # Then
        assert (
            retrieved_response
            == mocked_cache_management.retrieve_item_from_cache.return_value
        )

    @mock.patch(f"{MODULE_PATH}._calculate_response_and_save_in_cache")
    def test_does_not_recalculate_response_if_already_available(
        self, spy_calculate_response_and_save_in_cache: mock.MagicMock
    ):
        """
        Given a mocked request and a `CacheManagement` object
            which returns the expected response
        When `_retrieve_response_from_cache_or_calculate()` is called
        Then `_calculate_response_from_view()` is not called

        Patches:
            `spy_calculate_response_and_save_in_cache`: For the main assertion
        """
        mocked_request = mock.MagicMock(
            method="POST", headers={CACHE_FORCE_REFRESH_HEADER_KEY: False}
        )
        mocked_cache_management = mock.Mock()

        # When
        _retrieve_response_from_cache_or_calculate(
            mock.Mock(),  # view_function
            None,  # timeout
            mock.Mock(),
            mocked_request,
            cache_management=mocked_cache_management,
        )

        # Then
        spy_calculate_response_and_save_in_cache.assert_not_called()

    # Tests for cache misses + no force refreshing

    @mock.patch(f"{MODULE_PATH}._calculate_response_and_save_in_cache")
    def test_recalculates_response_when_not_available(
        self,
        spy_calculate_response_and_save_in_cache: mock.MagicMock,
    ):
        """
        Given a mocked request which will miss the cache
        When `_retrieve_response_from_cache_or_calculate()` is called
        Then `_calculate_response_and_save_in_cache()` is called with the correct args

        Patches:
            `spy_calculate_response_and_save_in_cache`: For the main assertion
        """
        # Given
        mocked_request = mock.MagicMock(
            method="POST", headers={CACHE_FORCE_REFRESH_HEADER_KEY: False}
        )
        mocked_view_function = mock.Mock()
        mocked_cache_management = mock.Mock()
        mocked_args = [mock.Mock(), mocked_request, mock.Mock()]
        mocked_kwargs = {"cache_management": mocked_cache_management}
        mocked_cache_management.retrieve_item_from_cache.side_effect = [CacheMissError]

        # When
        retrieved_response = _retrieve_response_from_cache_or_calculate(
            mocked_view_function, None, *mocked_args, **mocked_kwargs
        )

        # Then
        expected_cache_entry_key = (
            mocked_cache_management.build_cache_entry_key_for_request.return_value
        )
        spy_calculate_response_and_save_in_cache.assert_called_with(
            mocked_view_function,
            None,  # timeout
            mocked_cache_management,
            expected_cache_entry_key,
            *mocked_args,
        )

        assert (
            retrieved_response == spy_calculate_response_and_save_in_cache.return_value
        )

    # Tests for force refreshing

    @mock.patch(f"{MODULE_PATH}._calculate_response_and_save_in_cache")
    def test_force_refresh_header_means_response_is_recalculated_and_saved_if_already_available(
        self, spy_calculate_response_and_save_in_cache: mock.MagicMock
    ):
        """
        Given a mocked request and a `CacheManagement` object
            which will return a valid pre-calculated response
        When `_retrieve_response_from_cache_or_calculate()` is called
        Then the response is recalculated and saved regardless

        Patches:
            `spy_calculate_response_and_save_in_cache`: For the main assertion
        """
        # Given
        mocked_request = mock.MagicMock(
            method="POST", headers={CACHE_FORCE_REFRESH_HEADER_KEY: True}
        )
        mocked_cache_management = mock.Mock()
        mocked_cache_management.retrieve_item_from_cache = mock.Mock()

        # When
        retrieved_response = _retrieve_response_from_cache_or_calculate(
            mock.Mock(),  # view_function
            None,  # timeout
            mock.Mock(),
            mocked_request,
            cache_management=mocked_cache_management,
        )

        # Then
        assert (
            retrieved_response
            == spy_calculate_response_and_save_in_cache.return_value
            != mocked_cache_management.retrieve_item_from_cache.return_value
        )

    @mock.patch(f"{MODULE_PATH}._calculate_response_and_save_in_cache")
    def test_force_refresh_header_means_response_is_recalculated_and_saved_if_not_available(
        self, spy_calculate_response_and_save_in_cache: mock.MagicMock
    ):
        """
        Given a mocked request and a `CacheManagement` object
            which will not return a valid pre-calculated response
        When `_retrieve_response_from_cache_or_calculate()` is called
        Then the response is recalculated and saved

        Patches:
            `spy_calculate_response_and_save_in_cache`: For the main assertion
        """
        # Given
        mocked_request = mock.MagicMock(
            method="POST", headers={CACHE_FORCE_REFRESH_HEADER_KEY: True}
        )
        mocked_cache_management = mock.Mock()
        mocked_cache_management.retrieve_item_from_cache.side_effect = [CacheMissError]

        # When
        retrieved_response = _retrieve_response_from_cache_or_calculate(
            mock.Mock(),  # view_function
            None,  # timeout
            mock.Mock(),
            mocked_request,
            cache_management=mocked_cache_management,
        )

        # Then
        spy_calculate_response_and_save_in_cache.assert_called_once()
        assert (
            retrieved_response == spy_calculate_response_and_save_in_cache.return_value
        )

    # Tests for cache checking only

    def test_cache_checking_only_raises_error_if_cache_miss(self):
        """
        Given a `Cache-Check` header of True and no pre-saved items in the cache
        When `_retrieve_response_from_cache_or_calculate()` is called
        Then a `CacheCheckResultedInMissError()` is raised
        """
        # Given
        mocked_request = mock.MagicMock(
            method="POST", headers={CACHE_CHECK_HEADER_KEY: True}
        )
        mocked_cache_management = mock.Mock()
        mocked_cache_management.retrieve_item_from_cache.side_effect = [CacheMissError]

        # When / Then
        with pytest.raises(CacheCheckResultedInMissError):
            _retrieve_response_from_cache_or_calculate(
                mock.Mock(),  # view_function
                None,  # timeout
                mock.Mock(),
                mocked_request,
                cache_management=mocked_cache_management,
            )

    @mock.patch(f"{MODULE_PATH}._calculate_response_and_save_in_cache")
    @mock.patch(f"{MODULE_PATH}._calculate_response_from_view")
    @mock.patch(f"{MODULE_PATH}.is_caching_v2_enabled")
    def test_item_not_cached_when_caching_v2_enabled_is_set_to_true(
        self,
        mocked_is_caching_v2_enabled: mock.MagicMock,
        spy_calculate_response_from_view: mock.MagicMock,
        spy_calculate_response_and_save_in_cache: mock.MagicMock,
    ):
        """
        Given a mocked request and `is_caching_v2_enabled()` returns True
        When `_retrieve_response_from_cache_or_calculate()` is called
        Then the response is calculated and not saved

        Patches:
            `spy_calculate_response_from_view`: For the main assertion
            `spy_calculate_response_and_save_in_cache`: To check that
                the response is not being saved to the cache

        """
        # Given
        mocked_is_caching_v2_enabled.return_value = True
        mocked_request = mock.MagicMock(method="POST")
        mocked_view_function = mock.Mock()
        mocked_args = mock.Mock()

        # When
        retrieved_response = _retrieve_response_from_cache_or_calculate(
            mocked_view_function,  # view_function
            None,  # timeout
            mocked_args,
            mocked_request,
            cache_management=mock.Mock(),
        )

        # Then
        spy_calculate_response_and_save_in_cache.assert_not_called()
        spy_calculate_response_from_view.assert_called_once()
        assert retrieved_response == spy_calculate_response_from_view.return_value


class TestCalculateResponseAndSaveInCache:
    @mock.patch(f"{MODULE_PATH}._calculate_response_from_view")
    def test_delegates_call_to_calculate_response_from_view(
        self, spy_calculate_response_from_view: mock.MagicMock
    ):
        """
        Given a view function
        When `_calculate_response_and_save_in_cache()`
        Then the call is delegated to `_calculate_response_from_view()`
            so that the response can be calculated from the view function

        Patches:
            `spy_calculate_response_from_view`: For the main assertion
        """
        # Given
        mocked_view_function = mock.Mock()
        spy_cache_management = mock.Mock()
        fake_cache_entry_key = "abc"
        mocked_args = [mock.Mock(), mock.Mock()]
        mocked_kwargs = {"key_a": mock.Mock(), "key_b": mock.Mock}

        # When
        response = _calculate_response_and_save_in_cache(
            mocked_view_function,
            None,  # timeout
            spy_cache_management,
            fake_cache_entry_key,
            *mocked_args,
            **mocked_kwargs,
        )

        # Then
        spy_calculate_response_from_view.assert_called_once_with(
            mocked_view_function, *mocked_args, **mocked_kwargs
        )
        assert response == spy_calculate_response_from_view.return_value

    @mock.patch(f"{MODULE_PATH}._calculate_response_from_view")
    def test_delegates_call_to_save_item_in_cache(
        self, spy_calculate_response_from_view: mock.MagicMock
    ):
        """
        Given a mocked `CacheManagement`
        When `_calculate_response_and_save_in_cache()`
        Then the call is delegated  to the `save_item_in_cache()`
            method on the `CacheManagement` object

        Patches:
            `spy_calculate_response_from_view`: To isolate
                the expected response which has been calculated
                so that it can be checked to have been
                passed to `save_item_in_cache()`
        """
        # Given
        mocked_view_function = mock.Mock()
        spy_cache_management = mock.Mock()
        fake_cache_entry_key = "abc"
        mocked_args = [mock.Mock(), mock.Mock()]
        mocked_kwargs = {"key_a": mock.Mock(), "key_b": mock.Mock}

        # When
        _calculate_response_and_save_in_cache(
            mocked_view_function,
            123,  # timeout
            spy_cache_management,
            fake_cache_entry_key,
            *mocked_args,
            **mocked_kwargs,
        )

        # Then
        expected_calculated_response = spy_calculate_response_from_view.return_value
        spy_cache_management.save_item_in_cache.assert_called_once_with(
            cache_entry_key=fake_cache_entry_key,
            item=expected_calculated_response,
            timeout=123,
        )
